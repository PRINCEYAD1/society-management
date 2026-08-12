from django.conf import settings
from django.db import models
from core.models import Flat


class Vehicle(models.Model):
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name='vehicles')
    owner_name = models.CharField(max_length=120)
    vehicle_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=30, choices=[('CAR','Car'),('BIKE','Bike'),('OTHER','Other')], default='CAR')
    parking_slot = models.CharField(max_length=30, blank=True)
    photo = models.ImageField(upload_to='vehicles/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.vehicle_number} - {self.flat}'


class Parcel(models.Model):
    class Status(models.TextChoices):
        RECEIVED = 'RECEIVED', 'Received at Gate'
        NOTIFIED = 'NOTIFIED', 'Resident Notified'
        COLLECTED = 'COLLECTED', 'Collected'

    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name='parcels')
    recipient_name = models.CharField(max_length=120)
    courier_name = models.CharField(max_length=100, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='parcels/', blank=True, null=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.RECEIVED)
    received_at = models.DateTimeField(auto_now_add=True)
    collected_at = models.DateTimeField(blank=True, null=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f'{self.recipient_name} - {self.flat}'


class VendorAMC(models.Model):
    service_name = models.CharField(max_length=120)
    vendor_name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    start_date = models.DateField()
    renewal_date = models.DateField()
    document = models.FileField(upload_to='vendor_amc/', blank=True, null=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['renewal_date']

    def __str__(self):
        return f'{self.service_name} - {self.vendor_name}'


class Expense(models.Model):
    CATEGORY_CHOICES = [('UTILITIES','Utilities'),('REPAIR','Repair & Maintenance'),('SALARY','Salary'),('VENDOR','Vendor'),('EVENT','Event'),('OTHER','Other')]
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expense_date = models.DateField()
    vendor = models.CharField(max_length=150, blank=True)
    receipt = models.ImageField(upload_to='expense_receipts/', blank=True, null=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        ordering = ['-expense_date']

    def __str__(self):
        return self.title


class MoveRequest(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'REQUESTED', 'Requested'
        APPROVED = 'APPROVED', 'Approved'
        COMPLETED = 'COMPLETED', 'Completed'
        REJECTED = 'REJECTED', 'Rejected'

    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name='move_requests')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    move_type = models.CharField(max_length=10, choices=[('MOVE_IN','Move In'),('MOVE_OUT','Move Out')])
    requested_date = models.DateField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.REQUESTED)
    document = models.FileField(upload_to='move_requests/', blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.get_move_type_display()} - {self.flat}'


class DomesticWorker(models.Model):
    SERVICE_CHOICES = [('MAID','Maid'),('DRIVER','Driver'),('COOK','Cook'),('CLEANER','Cleaner'),('TUTOR','Tutor'),('OTHER','Other')]
    name = models.CharField(max_length=120)
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES, default='MAID')
    phone = models.CharField(max_length=20, blank=True)
    id_number = models.CharField(max_length=80, blank=True)
    flats = models.ManyToManyField(Flat, related_name='domestic_workers', blank=True)
    photo = models.ImageField(upload_to='domestic_workers/', blank=True, null=True)
    id_document = models.FileField(upload_to='domestic_worker_docs/', blank=True, null=True)
    police_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name} ({self.get_service_type_display()})'


class StaffAttendance(models.Model):
    worker = models.ForeignKey(DomesticWorker, on_delete=models.CASCADE, related_name='attendance')
    check_in = models.DateTimeField(auto_now_add=True)
    check_out = models.DateTimeField(blank=True, null=True)
    gate_note = models.CharField(max_length=200, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        ordering = ['-check_in']


class CertificateRequest(models.Model):
    TYPE_CHOICES = [('NOC','NOC'),('ADDRESS','Address Proof'),('TENANT','Tenant Verification Letter'),('PARKING','Parking Certificate'),('OTHER','Other')]
    STATUS_CHOICES = [('PENDING','Pending'),('APPROVED','Approved'),('REJECTED','Rejected'),('ISSUED','Issued')]
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificate_requests')
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name='certificate_requests')
    request_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    purpose = models.TextField(blank=True)
    supporting_document = models.FileField(upload_to='certificate_requests/', blank=True, null=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='PENDING')
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-requested_at']


class SocietyMeeting(models.Model):
    title = models.CharField(max_length=160)
    meeting_date = models.DateTimeField()
    venue = models.CharField(max_length=160, blank=True)
    agenda = models.TextField(blank=True)
    minutes = models.TextField(blank=True)
    attachment = models.FileField(upload_to='meetings/', blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        ordering = ['-meeting_date']


class Poll(models.Model):
    question = models.CharField(max_length=220)
    description = models.TextField(blank=True)
    closes_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question


class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    label = models.CharField(max_length=120)

    def __str__(self):
        return self.label


class PollVote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='votes')
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['poll','user'], name='one_vote_per_user_per_poll')]


class SocietyAsset(models.Model):
    CATEGORY_CHOICES = [('CCTV','CCTV'),('LIFT','Lift'),('PUMP','Pump'),('GENERATOR','Generator'),('FIRE','Fire Safety'),('GYM','Gym Equipment'),('OTHER','Other')]
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    asset_code = models.CharField(max_length=60, unique=True)
    location = models.CharField(max_length=150, blank=True)
    purchase_date = models.DateField(blank=True, null=True)
    warranty_until = models.DateField(blank=True, null=True)
    next_service_date = models.DateField(blank=True, null=True)
    document = models.FileField(upload_to='assets/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.asset_code} - {self.name}'


class EmergencyContact(models.Model):
    CATEGORY_CHOICES = [('AMBULANCE','Ambulance'),('HOSPITAL','Hospital'),('POLICE','Police'),('FIRE','Fire Brigade'),('ELECTRICIAN','Electrician'),('PLUMBER','Plumber'),('OTHER','Other')]
    name = models.CharField(max_length=140)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    phone = models.CharField(max_length=25)
    secondary_phone = models.CharField(max_length=25, blank=True)
    notes = models.CharField(max_length=220, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category','name']


class LostFoundItem(models.Model):
    TYPE_CHOICES = [('LOST','Lost'),('FOUND','Found')]
    STATUS_CHOICES = [('OPEN','Open'),('CLAIMED','Claimed'),('CLOSED','Closed')]
    item_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    title = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=140, blank=True)
    photo = models.ImageField(upload_to='lost_found/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    reported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-reported_at']


class SocietyEvent(models.Model):
    title = models.CharField(max_length=160)
    event_date = models.DateTimeField()
    venue = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    poster = models.ImageField(upload_to='events/', blank=True, null=True)
    registration_required = models.BooleanField(default=False)
    contribution_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['event_date']

    def __str__(self):
        return self.title
