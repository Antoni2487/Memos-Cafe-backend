from decimal import Decimal

from django.db import migrations


CATEGORIA_NOMBRE = "Descartables"

DESCARTABLES = [
    {"nombre": "Descartable S/1.00", "precio": Decimal("1.00")},
    {"nombre": "Descartable S/0.50", "precio": Decimal("0.50")},
]


def crear_descartables(apps, schema_editor):
    Categoria = apps.get_model("productos", "Categoria")
    Producto = apps.get_model("productos", "Producto")

    categoria, _ = Categoria.objects.get_or_create(
        nombre=CATEGORIA_NOMBRE, defaults={"activo": True}
    )

    for datos in DESCARTABLES:
        Producto.objects.get_or_create(
            nombre=datos["nombre"],
            categoria=categoria,
            defaults={
                "descripcion": "Envase/bolsa descartable para pedidos.",
                "precio": datos["precio"],
                "disponible": True,
            },
        )


def eliminar_descartables(apps, schema_editor):
    Categoria = apps.get_model("productos", "Categoria")
    Producto = apps.get_model("productos", "Producto")
    Producto.objects.filter(
        categoria__nombre=CATEGORIA_NOMBRE,
        nombre__in=[d["nombre"] for d in DESCARTABLES],
    ).delete()
    Categoria.objects.filter(nombre=CATEGORIA_NOMBRE, productos__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("productos", "0002_remove_producto_imagen_url_and_more"),
    ]

    operations = [
        migrations.RunPython(crear_descartables, eliminar_descartables),
    ]
