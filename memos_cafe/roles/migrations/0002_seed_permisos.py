from django.db import migrations


# Espeja el comportamiento que ya tenia el sistema antes de que PermisoRol
# se conectara a la autorizacion real (grupos de Django), mas la unica
# restriccion que el admin ya habia configurado manualmente: mesero y
# cajero sin acceso al modulo de gestion de Mesas.
VALORES = {
    "dashboard": {"admin": True,  "cajero": True,  "mesero": True},
    "mesas":     {"admin": True,  "cajero": False, "mesero": False},
    "ordenes":   {"admin": True,  "cajero": True,  "mesero": True},
    "caja":      {"admin": True,  "cajero": True,  "mesero": False},
    "productos": {"admin": True,  "cajero": False, "mesero": False},
    "insumos":   {"admin": True,  "cajero": False, "mesero": False},
    "reportes":  {"admin": True,  "cajero": False, "mesero": False},
    "usuarios":  {"admin": True,  "cajero": False, "mesero": False},
}


def sembrar_permisos(apps, schema_editor):
    PermisoRol = apps.get_model("roles", "PermisoRol")
    for modulo, por_rol in VALORES.items():
        for rol, puede_acceder in por_rol.items():
            PermisoRol.objects.get_or_create(
                modulo=modulo, rol=rol,
                defaults={"puede_acceder": puede_acceder},
            )


def eliminar_permisos(apps, schema_editor):
    PermisoRol = apps.get_model("roles", "PermisoRol")
    for modulo, por_rol in VALORES.items():
        PermisoRol.objects.filter(modulo=modulo, rol__in=por_rol.keys()).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("roles", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(sembrar_permisos, eliminar_permisos),
    ]
