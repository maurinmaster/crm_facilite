import uuid
from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.utils import timezone

from openpyxl import Workbook

from .auth import authenticate, create_session, destroy_session
from .models import Client, ClientContact, ClientCredentialSimple, ClientLink


def require_login(request):
    if not getattr(request, 'user_ctx', None):
        return redirect('/login/?next=' + request.path)
    return None


def home(request):
    return redirect('/clients/')


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html', { 'next': request.GET.get('next', '/clients/'), 'error': None })

    email = request.POST.get('email', '')
    password = request.POST.get('password', '')
    nxt = request.POST.get('next', '/clients/')

    u = authenticate(email, password)
    if not u:
        return render(request, 'login.html', { 'next': nxt, 'error': 'Credenciais inválidas' })

    token, exp = create_session(u.id)
    resp = redirect(nxt or '/clients/')
    resp.set_cookie('crm_session', token, httponly=True, secure=True, samesite='Lax', path='/', max_age=60*60*24*14)
    return resp


@require_http_methods(["POST", "GET"])
def logout_view(request):
    tok = request.COOKIES.get('crm_session')
    destroy_session(tok)
    resp = redirect('/login/')
    resp.delete_cookie('crm_session', path='/')
    return resp


def clients_list(request):
    guard = require_login(request)
    if guard: return guard

    q = (request.GET.get('q') or '').strip()
    page = int(request.GET.get('page') or '1')

    qs = Client.objects.all().order_by('name')
    if q:
        qs = qs.filter(name__icontains=q)

    paginator = Paginator(qs, 25)
    p = paginator.get_page(page)

    return render(request, 'clients.html', {
        'q': q,
        'page_obj': p,
    })


def client_detail(request, client_id):
    guard = require_login(request)
    if guard: return guard

    c = Client.objects.filter(id=client_id).first()
    if not c:
        return HttpResponse('Not found', status=404)

    contacts = ClientContact.objects.filter(client_id=client_id).order_by('-created_at')
    creds = ClientCredentialSimple.objects.filter(client_id=client_id).order_by('-created_at')
    links = ClientLink.objects.filter(client_id=client_id).order_by('-created_at')

    return render(request, 'client_detail.html', {
        'client': c,
        'contacts': contacts,
        'creds': creds,
        'links': links,
    })


@require_http_methods(["GET", "POST"])
def client_new(request):
    guard = require_login(request)
    if guard: return guard

    if request.method == 'GET':
        return render(request, 'client_form.html', { 'title': 'Novo cliente', 'client': {}, 'error': None })

    cid = str(uuid.uuid4())
    name = (request.POST.get('name') or '').strip()
    if not name:
        return render(request, 'client_form.html', { 'title': 'Novo cliente', 'client': request.POST, 'error': 'Nome obrigatório' })

    Client.objects.create(
        id=cid,
        name=name,
        cnpj=(request.POST.get('cnpj') or '').strip() or None,
        status=(request.POST.get('status') or '').strip() or None,
        type=(request.POST.get('type') or '').strip() or None,
        notes=(request.POST.get('notes') or '').strip() or None,
        created_at=timezone.now(),
        updated_at=timezone.now(),
    )
    return redirect(f'/clients/{cid}/')


@require_http_methods(["GET", "POST"])
def client_edit(request, client_id):
    guard = require_login(request)
    if guard: return guard

    c = Client.objects.filter(id=client_id).first()
    if not c:
        return HttpResponse('Not found', status=404)

    if request.method == 'GET':
        return render(request, 'client_form.html', { 'title': 'Editar cliente', 'client': c, 'error': None })

    name = (request.POST.get('name') or '').strip()
    if not name:
        return render(request, 'client_form.html', { 'title': 'Editar cliente', 'client': c, 'error': 'Nome obrigatório' })

    c.name = name
    c.cnpj = (request.POST.get('cnpj') or '').strip() or None
    c.status = (request.POST.get('status') or '').strip() or None
    c.type = (request.POST.get('type') or '').strip() or None
    c.notes = (request.POST.get('notes') or '').strip() or None
    c.updated_at = timezone.now()
    c.save(update_fields=['name', 'cnpj', 'status', 'type', 'notes', 'updated_at'])

    return redirect(f'/clients/{client_id}/')


@require_http_methods(["POST"])
def client_delete(request, client_id):
    guard = require_login(request)
    if guard: return guard

    Client.objects.filter(id=client_id).delete()
    ClientContact.objects.filter(client_id=client_id).delete()
    ClientCredentialSimple.objects.filter(client_id=client_id).delete()
    ClientLink.objects.filter(client_id=client_id).delete()
    return redirect('/clients/')


@require_http_methods(["POST"])
def contact_new(request, client_id):
    guard = require_login(request)
    if guard: return guard

    ClientContact.objects.create(
        id=str(uuid.uuid4()),
        client_id=client_id,
        name=(request.POST.get('name') or '').strip() or None,
        role=(request.POST.get('role') or '').strip() or None,
        department=(request.POST.get('department') or '').strip() or None,
        phone=(request.POST.get('phone') or '').strip() or None,
        email=(request.POST.get('email') or '').strip() or None,
        instagram=(request.POST.get('instagram') or '').strip() or None,
        notes=(request.POST.get('notes') or '').strip() or None,
        created_at=timezone.now(),
    )
    return redirect(f'/clients/{client_id}/')


@require_http_methods(["POST"])
def contact_delete(request, contact_id):
    guard = require_login(request)
    if guard: return guard

    c = ClientContact.objects.filter(id=contact_id).first()
    if not c:
        return redirect('/clients/')
    client_id = c.client_id
    ClientContact.objects.filter(id=contact_id).delete()
    return redirect(f'/clients/{client_id}/')


@require_http_methods(["POST"])
def cred_new(request, client_id):
    guard = require_login(request)
    if guard: return guard

    ClientCredentialSimple.objects.create(
        id=str(uuid.uuid4()),
        client_id=client_id,
        site=(request.POST.get('site') or '').strip() or None,
        usuario=(request.POST.get('usuario') or '').strip() or None,
        senha=(request.POST.get('senha') or '').strip() or None,
        token=(request.POST.get('token') or '').strip() or None,
        obs=(request.POST.get('obs') or '').strip() or None,
        created_at=timezone.now(),
    )
    return redirect(f'/clients/{client_id}/')


@require_http_methods(["POST"])
def cred_delete(request, cred_id):
    guard = require_login(request)
    if guard: return guard

    c = ClientCredentialSimple.objects.filter(id=cred_id).first()
    if not c:
        return redirect('/clients/')
    client_id = c.client_id
    ClientCredentialSimple.objects.filter(id=cred_id).delete()
    return redirect(f'/clients/{client_id}/')


@require_http_methods(["POST"])
def link_new(request, client_id):
    guard = require_login(request)
    if guard: return guard

    ClientLink.objects.create(
        id=str(uuid.uuid4()),
        client_id=client_id,
        name=(request.POST.get('name') or '').strip() or None,
        url=(request.POST.get('url') or '').strip() or None,
        created_at=timezone.now(),
    )
    return redirect(f'/clients/{client_id}/')


@require_http_methods(["POST"])
def link_delete(request, link_id):
    guard = require_login(request)
    if guard: return guard

    l = ClientLink.objects.filter(id=link_id).first()
    if not l:
        return redirect('/clients/')
    client_id = l.client_id
    ClientLink.objects.filter(id=link_id).delete()
    return redirect(f'/clients/{client_id}/')


def export_xlsx(request):
    guard = require_login(request)
    if guard: return guard

    wb = Workbook()

    def norm(v):
        # openpyxl can't handle tz-aware datetimes
        try:
            if hasattr(v, 'tzinfo') and v.tzinfo is not None:
                return v.replace(tzinfo=None)
        except Exception:
            pass
        return v

    def add_sheet(name, rows, headers):
        ws = wb.create_sheet(title=name)
        ws.append(headers)
        for r in rows:
            ws.append([norm(getattr(r, h)) for h in headers])

    # Remove default sheet
    wb.remove(wb.active)

    add_sheet('clients', Client.objects.all().order_by('name'), ['id','org_id','name','cnpj','status','type','notes','updated_at','created_at'])
    add_sheet('client_contacts', ClientContact.objects.all().order_by('-created_at'), ['id','client_id','name','role','department','phone','email','instagram','notes','created_at'])
    add_sheet('client_credentials_simple', ClientCredentialSimple.objects.all().order_by('-created_at'), ['id','client_id','site','usuario','senha','token','obs','created_at'])
    add_sheet('client_links', ClientLink.objects.all().order_by('-created_at'), ['id','client_id','name','url','created_at'])

    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)

    resp = HttpResponse(
        bio.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    resp['Content-Disposition'] = 'attachment; filename="crm_facilite_export.xlsx"'
    return resp
