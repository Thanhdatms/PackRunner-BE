# from django.contrib import admin
# from django.contrib.auth.models import Group, Permission
# from django.contrib.contenttypes.models import ContentType

# def setup_groups():
#     admin_group, _ = Group.objects.get_or_create(name='Admin')
#     employee_group, _ = Group.objects.get_or_create(name='Employee')
#     user_group, _ = Group.objects.get_or_create(name='User')

#     content_type = ContentType.objects.get_for_model(Group)

#     view_report_perm, _ = Permission.objects.get_or_create(
#         codename='can_view_report',
#         name='Can View Report',
#         content_type=content_type,
#     )

#     edit_report_perm, _ = Permission.objects.get_or_create(
#         codename='can_edit_report',
#         name='Can Edit Report',
#         content_type=content_type,
#     )

#     edit_shipping_perm, _ = Permission.objects.get_or_create(
#         codename='can_change_shipping',
#         name='Can Change Shipping',
#         content_type=content_type,
#     )

#     admin_group.permissions.add(view_report_perm, edit_report_perm, edit_shipping_perm)
#     employee_group.permissions.add(view_report_perm, edit_shipping_perm)

# setup_groups()