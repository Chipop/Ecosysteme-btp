from .models import GroupeDroit, Droit, Admin


def admin_logged_in(request):
    if request.session.get('id_admin', None) is None:
        return False
    return True


def admin_has_permission(permission, groupe, request):
    if not admin_logged_in(request):
        return False

    admin = Admin.objects.get(id=request.session.get('id_admin'))

    groupe = GroupeDroit.objects.get(nom=groupe)
    droit = Droit.objects.get(nom=permission, groupe=groupe)

    if droit in admin.droits.all():
        return True
    return False



def get_object_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


def admin_logged(request):
    return Admin.objects.get(id=request.session['id_admin'])