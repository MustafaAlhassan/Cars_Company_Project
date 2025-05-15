from django.shortcuts import render, redirect
from .models import Car, Admins, Inventory, Financial
from .models import Car
from django.db.models import Count
from django.db.models import Sum
from django.contrib.auth.hashers import make_password, check_password

# Create your views here.

def index(request):
    top_five_cars = Car.objects.exclude(SellingPrice__isnull=True)\
        .values('car_name')\
        .annotate(count=Count('car_name'))\
        .order_by('-count')[:5]

    total_sold_cars = Car.objects.exclude(SellingPrice__isnull=True).count()
    total_exist_cars = Car.objects.exclude(SellingPrice__isnull=False).count()
    
    # Calculate total profits
    total_profits = Financial.objects.aggregate(total=Sum('profits'))['total'] or 0
    
    return render(request, 'index.html', {
        'top_sold_cars': top_five_cars, 
        'total_sold_cars': total_sold_cars, 
        'total_exist_cars': total_exist_cars,
        'total_profits': total_profits
    })

def cars(request):
    cars = Car.objects.all()
    inventory = Inventory.objects.all()
    return render(request, 'cars.html', {'cars': cars, 'inventory': inventory})

def loginPage(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            admin = Admins.objects.get(email=email)
            if check_password(password, admin.user_password):
                # Store admin info in session
                request.session['admin_id'] = admin.admin_id
                request.session['is_manager'] = admin.is_manager
                request.session['email'] = admin.email
                top_five_cars = Car.objects.exclude(SellingPrice__isnull=True)\
                .values('car_name')\
                .annotate(count=Count('car_name'))\
                .order_by('-count')[:5]

                total_sold_cars = Car.objects.exclude(SellingPrice__isnull=True).count()
                total_exist_cars = Car.objects.exclude(SellingPrice__isnull=False).count()
                
                # Calculate total profits
                total_profits = Financial.objects.aggregate(total=Sum('profits'))['total'] or 0
                
                return render(request, 'index.html', {
                    'top_sold_cars': top_five_cars, 
                    'total_sold_cars': total_sold_cars, 
                    'total_exist_cars': total_exist_cars,
                    'total_profits': total_profits
                })
            else:
                return render(request, 'login_page.html', {'error': 'Invalid password!'})
        except Admins.DoesNotExist:
            return render(request, 'login_page.html', {'error': 'Invalid Email!'})
            
    return render(request, 'login_page.html')
    

def logout(request):
    # Clear the session
    request.session.flush()
    return redirect('loginPage')

def change_password(request):
    if 'admin_id' not in request.session:
        return redirect('loginPage')
        
    if request.method == "POST":
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        verify_password = request.POST.get('verify_password')
        
        try:
            admin = Admins.objects.get(admin_id=request.session['admin_id'])
            if check_password(current_password, admin.user_password):
                if new_password == verify_password:
                    admin.user_password = make_password(new_password)
                    admin.save()
                    return render(request, 'settings.html', {'password_changed': "Password changed successfully!"})
                else:
                    return render(request, 'settings.html', {'password_not_changed': "New passwords do not match!"})
            else:
                return render(request, 'settings.html', {'password_not_changed': "Current password is incorrect!"})
        except Admins.DoesNotExist:
            return render(request, 'settings.html', {'password_not_changed': "Admin not found!"})
            
    return render(request, 'settings.html')

def remove_admin(request):
    if 'admin_id' not in request.session:
        return render(request, 'login_page.html')

    if request.method == "POST":
        password = request.POST.get('password')
        remove_email = request.POST.get('remove_email')

        try:
            current_admin = Admins.objects.get(admin_id=request.session['admin_id'])

            # Manager removes by email
            if current_admin.is_manager and remove_email:
                try:
                    admin_to_delete = Admins.objects.get(email=remove_email)
                    if admin_to_delete.admin_id == current_admin.admin_id:
                        return render(request, 'settings.html', {'admin_not_removed': "Managers cannot remove themselves!"})
                    elif check_password(password, current_admin.user_password):
                        admin_to_delete.delete()
                        return render(request, 'settings.html', {'admin_removed': "Admin removed successfully!"})
                    else:
                        return render(request, 'settings.html', {'admin_not_removed': "Invalid manager password!"})
                except Admins.DoesNotExist:
                    return render(request, 'settings.html', {'admin_not_removed': "Admin with this email does not exist!"})
            # ... (existing logic for regular admins or other cases)
        except Admins.DoesNotExist:
            return render(request, 'settings.html', {'admin_not_removed': "Current admin not found!"})

def add_admin(request):
    if 'admin_id' not in request.session or not request.session['is_manager']:
        return render(request, 'login_page.html')
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        verify_password = request.POST.get('verify')
        is_manager = request.POST.get('is_manager') == 'on'
        
        # Check if admin with this email already exists
        if Admins.objects.filter(email=email).exists():
            return render(request, 'settings.html', {'admin_not_added': "Admin with this email already exists!"})
        
        if password != verify_password:
            return render(request, 'settings.html', {'admin_not_added': "New passwords do not match!"})
            
        hashed_password = make_password(password)
        
        admin = Admins.objects.create(
            email=email,
            user_password=hashed_password,
            is_manager=is_manager
        )
        
        return render(request, 'settings.html', {'admin_added': "Admin added successfully!"})
        
    return render(request, 'settings.html')

def manage(request):
    return render(request, 'manage.html')

def settings(request):
    admins = Admins.objects.filter(is_manager=False)
    return render(request, 'settings.html', {'admins': admins})

def sold(request):
    cars = Car.objects.all()
    inventory = Inventory.objects.all()
    return render(request, 'sold.html', {'cars': cars, 'inventory': inventory})

def add_car(request):
    if request.method == "POST":
        car_name = request.POST.get('car_name')
        year_manufacture = request.POST.get('year_manufacture')
        car_type = request.POST.get('car_type')
        chassis = request.POST.get('chassis')
        car_color = request.POST.get('car_color')
        car_state = request.POST.get('car_state')
        car_metric = request.POST.get('car_metric')
        purchase_price = request.POST.get('purchase_price')
        purchase_date = request.POST.get('purchase_date')
        location = request.POST.get('location')

        # Check if chassis already exists
        if Car.objects.filter(chassis=chassis).exists():
            return render(request, 'manage.html', {'car_not_added': "Car with this chassis already exists!"})

        # Insert Car
        car = Car.objects.create(
            car_name=car_name,
            year_manufacture=year_manufacture,
            car_type=car_type,
            chassis=chassis,
            car_color=car_color,
            car_state=car_state,
            car_metric=car_metric,
            PurchasePrice=purchase_price,
            PurchaseDateTime=purchase_date
        )

        # Insert Inventory
        Inventory.objects.create(
            car=car,
            location=location
        )

    return render(request, 'manage.html', {'car_added': "Car added successfully!"})

def remove_car(request):
    if request.method == "POST":
        chassis = request.POST.get('chassis')

        try:
            car = Car.objects.get(chassis=chassis)
            car.delete()
            return render(request, 'manage.html', {'car_removed': "Car removed successfully!"})
        except Car.DoesNotExist:
            return render(request, 'manage.html', {'car_not_removed': "Car with this chassis does not exist!"})

    return render(request, 'manage.html')

def sold_car(request):
    if request.method == 'POST':
        chassis = request.POST.get('chassis')
        selling_price = request.POST.get('selling_price')
        selling_date = request.POST.get('selling_date')  # from form

        try:
            car = Car.objects.get(chassis=chassis)
            car.SellingPrice = selling_price
            car.SellingDateTime = selling_date  # if you want current time use timezone.now()
            car.save()
            
            # Calculate profit and save to Financial table
            if car.PurchasePrice is not None and car.SellingPrice is not None:
                profit = float(car.SellingPrice) - float(car.PurchasePrice)
                Financial.objects.create(
                    car=car,
                    profits=profit
                )
                
        except Car.DoesNotExist:
            return render(request, 'manage.html', {'car_not_sold': "Car with this chassis does not exist!"})

    return render(request, 'manage.html', {'car_sold': "Car sold successfully!"})

def modify_car(request):
    car = None
    location = None
    if request.method == 'POST':
        chassis = request.POST.get('chassis')
        if 'search' in request.POST:
            try:
                car = Car.objects.get(chassis=chassis)
                inventory = Inventory.objects.get(car=car)
                location = inventory.location
            except Car.DoesNotExist:
                return render(request, 'manage.html', {'car_not_modified': "Car with this chassis does not exist!"})
        elif 'update' in request.POST:
            try:
                car = Car.objects.get(chassis=chassis)
                car.car_name = request.POST.get('car_name')
                car.year_manufacture = request.POST.get('year_manufacture')
                car.car_type = request.POST.get('car_type')
                car.chassis = chassis
                car.car_color = request.POST.get('car_color')
                car.car_state = request.POST.get('car_state')
                car.car_metric = request.POST.get('car_metric')
                car.PurchasePrice = request.POST.get('purchase_price')
                car.SellingPrice = request.POST.get('selling_price')
                car.PurchaseDateTime = request.POST.get('purchase_date')
                car.SellingDateTime = request.POST.get('selling_date')
                # Update location in Inventory
                new_location = request.POST.get('location')
                inventory = Inventory.objects.get(car=car)
                inventory.location = new_location
                inventory.save()
                car.save()
                # Update profit in Financial if car is sold
                if car.PurchasePrice and car.SellingPrice:
                    profit = float(car.SellingPrice) - float(car.PurchasePrice)
                    # Update existing Financial record or create one if not exists
                    financial, created = Financial.objects.get_or_create(car=car)
                    financial.profits = profit
                    financial.save()
                return render(request, 'manage.html', {'car_modified': "Car updated successfully!"})
            except Car.DoesNotExist:
                return render(request, 'manage.html', {'car_not_modified': "Car with this chassis does not exist!"})
    return render(request, 'manage.html', {'car': car, 'location': location})