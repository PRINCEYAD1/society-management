from django.contrib import admin
from .models import Vehicle, Parcel, VendorAMC, Expense, MoveRequest

admin.site.register(Vehicle)
admin.site.register(Parcel)
admin.site.register(VendorAMC)
admin.site.register(Expense)
admin.site.register(MoveRequest)
