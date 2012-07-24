from django.core.paginator import Paginator, InvalidPage, EmptyPage

from django_snailtracker.models import Snailtrack, Action

def index(request):
    return {}

def table_index(request, table):
    st = Snailtrack(client=redis_factory())
    st.table = table
    pks = list(st.get_pks_for_table())
    paginator = Paginator(pks, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        pks = paginator.page(page)
    except (EmptyPage, InvalidPage):
        pks = paginator.page(paginator.num_pages)
    return {'table': table, 'pks': pks}

def view(request, table=None, pk=None):
    st = Snailtrack(client=redis_factory())
    try:
        st.get(table=table, primary_key=pk)
    except:
        st = None
    return {'snailtrack':st}
