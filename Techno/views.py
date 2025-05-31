from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.http import HttpResponse
from django.contrib import messages
from datetime import date


def home(request):
    return render(request, "home.html")

def new_cust(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        location = request.POST.get('location', '').strip()
        phone = request.POST.get('phone', '').strip()
        gst_no = request.POST.get('gst_no', '').strip()

        if Customer.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'new_cust.html')
        if Customer.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'new_cust.html')
        if Customer.objects.filter(gst_no=gst_no).exists():
            messages.error(request, "GST Number already exists.")
            return render(request, 'new_cust.html')
        if Customer.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number already exists.")
            return render(request, 'reg_seeker.html')
        
        customer = Customer.objects.create(
            username=username,
            email=email,
            location=location,
            phone=phone,
            gst_no = gst_no
        )
        messages.success(request, "Registration successful!")
        return redirect('select_cust')
    return render(request, "new_cust.html")

def select_cust(request):
    customers = Customer.objects.all()

    if request.method == 'POST':
        customer_name = request.POST.get('customer', '').strip()
        no_thickness = request.POST.get('no_thickness', '').strip()

        if not Customer.objects.filter(username=customer_name).exists():
            messages.error(request, f"Customer '{customer_name}' does not exist.")
            return render(request, "select_cust.html", {'customers': customers})

        if not no_thickness.isdigit() or int(no_thickness) <= 0:
            messages.error(request, "Number of thickness types must be a positive number.")
            return render(request, "select_cust.html", {'customers': customers})

        customer = Customer.objects.get(username=customer_name)
        request.session['selected_customer_id'] = customer.id
        request.session['no_thickness'] = no_thickness

        return redirect('customer_profile_view', customer_id=customer.id)

    return render(request, "select_cust.html", {'customers': customers})



def customer_profile_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    return render(request, 'customer_profile.html', {'customer': customer})

def confirm_customer(request, customer_id):
    return redirect('thickness_select')



def thickness_select(request):
    # Clear previous measurement session data if the user reloads or revisits this page
    request.session.pop('all_measurements', None)
    request.session.pop('thickness_list', None)
    request.session.pop('current_thickness_index', None)
    request.session.pop('extra_charges', None)

    no_thickness = request.session.get('no_thickness')

    if not no_thickness:
        return redirect('select_cust')  # Redirect if missing

    try:
        no_thickness = int(no_thickness)
    except ValueError:
        return redirect('select_cust')

    if request.method == 'POST':
        selected_thicknesses = []
        for i in range(1, no_thickness + 1):
            value = request.POST.get(f'thickness_{i}')
            selected_thicknesses.append(value)

        request.session['thickness_list'] = selected_thicknesses
        request.session['current_thickness_index'] = 0
        return redirect('measurements')

    return render(request, 'thickness_select.html', {
        'no_thickness': range(no_thickness),
    })



def measurements(request):
    thickness_list = request.session.get('thickness_list', [])
    index = request.session.get('current_thickness_index', 0)

    if index >= len(thickness_list):
        return redirect('extra_charges')

    current_thickness = thickness_list[index]

    if request.method == 'POST':
        unit = request.POST.get('unit')
        measurements_1 = request.POST.getlist('measurement_1')
        measurements_2 = request.POST.getlist('measurement_2')

        measurements = list(zip(measurements_1, measurements_2))

        # Store measurements in session
        if 'all_measurements' not in request.session:
            request.session['all_measurements'] = []

        data = {
            'thickness': current_thickness,
            'unit': unit,
            'measurements': measurements,
        }

        request.session['all_measurements'].append(data)
        request.session.modified = True  # Important to save the list

        # Move to next thickness
        request.session['current_thickness_index'] = index + 1
        return redirect('measurements')

    return render(request, 'measurements.html', {
        'thickness': current_thickness
    })

def extra_charges(request):
    if request.method == 'POST':
        data = {
            'patch_cutting': request.POST.get('patch_cutting'),
            'hole': request.POST.get('hole'),
            'hole_big': request.POST.get('hole_big'),
            'l_shape': request.POST.get('l_shape'),
            'wheel_cut': request.POST.get('wheel_cut'),
            'shape_cut': request.POST.get('shape_cut'),
            'cut_out': request.POST.get('cut_out'),
            'beveling_charge': request.POST.get('beveling_charge'),
            'etching_work': request.POST.get('etching_work'),
            'cutting_charge': request.POST.get('cutting_charge'),
            'document_charge': request.POST.get('document_charge'),
            'handling_charge': request.POST.get('handling_charge'),
            'transportation': request.POST.get('transportation'),
            'cash_discount': request.POST.get('cash_discount'),
        }

        # Save or process data here
        request.session['extra_charges'] = data

        return redirect('template_page')  # Or wherever you want to go next

    return render(request, 'extra_charges.html')


RATE_PER_SQFT = {
    "12": 160,
    "10": 145,
    "8": 120,
    "6": 95,
    "5": 85,
    "4": 60,
}

# Converts area to sqft based on unit
def convert_to_sqft(width, height, unit):
    print (unit)
    unit = unit.lower()
    if unit == "cm":
        return (width * height) / 929.0304
    elif unit == "mm":
        return (width * height) / 92903.04
    elif unit == "inch":
        return (width * height) / 144
    elif unit in ("feet", "ft"):
        return width * height
    return 0  # Unknown unit


# Main view to render the summary
def safe_float(val, default=0.0):
    try:
        return float(val)
    except (TypeError, ValueError):
        return default

def template_page(request):
    all_data = request.session.get("all_measurements", [])
    extra_charges = request.session.get("extra_charges", {})
    customer_id = request.session.get("selected_customer_id")

    if not customer_id:
        return redirect('select_cust')  # Redirect if no customer selected

    customer = get_object_or_404(Customer, id=customer_id)

    for item in all_data:
        raw_thickness = str(item.get("thickness", "")).strip().replace("mm", "")
        thickness = raw_thickness
        rate = RATE_PER_SQFT.get(thickness, 0)

        unit = item.get("unit", "").lower()
        measurements = item.get("measurements", [])

        item["rate"] = rate

        calculated = []
        for m in measurements:
            if not m or len(m) < 2:
                continue  # Skip incomplete data

            width = safe_float(m[0])
            height = safe_float(m[1])
            area_sqft = convert_to_sqft(width, height, unit)
            total = round(area_sqft * rate, 2)
            calculated.append({
                "width": width,
                "height": height,
                "area": round(area_sqft, 2),
                "total": total
            })

        item["calculated_measurements"] = calculated

    context = {
        "customer": customer,
        "all_data": all_data,
        "extra_charges": {k: v for k, v in extra_charges.items() if v not in ("", None)},
        "today_date": date.today().strftime('%d-%m-%Y'),
    }

    return render(request, "template_page.html", context)


import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def save_and_print(request):
    if request.method == "POST":
        raw_data = request.POST.get("data")
        if not raw_data:
            return HttpResponse("No data", status=400)

        data = json.loads(raw_data)

        customer_id = data.get("customer_id")
        customer = Customer.objects.get(id=customer_id)

        # Create summary object
        summary = GlassSummary.objects.create(customer=customer)

        for item in data["data"]:
            thickness = item["thickness"]
            unit = item["unit"]
            for m in item["measurements"]:
                Measurement.objects.create(
                    customer=customer,
                    summary=summary,
                    thickness=thickness,
                    unit=unit,
                    height=m["height"],
                    width=m["width"],
                    quantity=m["quantity"],
                    area=m["area"],
                    rate=m["rate"],
                    amount=m["amount"],
                    shape=m["shape"],
                )

        for key, val in data["extra_charges"].items():
            if val:
                ExtraCharge.objects.create(
                    customer=customer,
                    summary=summary,
                    label=key,
                    amount=val,
                )

        return render(request, "print_page.html", {"message": "Saved. Now printing..."})

    return HttpResponse("Invalid request", status=400)


def summary_list_view(request):
    summaries = GlassSummary.objects.select_related('customer').order_by('-created_at')
    return render(request, 'summary_list.html', {'summaries': summaries})

def template_page_edit(request, summary_id):
    summary = get_object_or_404(GlassSummary, id=summary_id)
    customer = summary.customer

    # Get all measurements related to this summary
    measurements = summary.measurements.all().order_by('thickness')

    # Organize measurements thickness-wise
    all_data = {}
    for m in measurements:
        if m.thickness not in all_data:
            all_data[m.thickness] = []
        all_data[m.thickness].append(m)

    # Get all extra charges related to this summary
    extra_charges = {ec.label: ec.amount for ec in summary.extra_charges.all()}

    return render(request, 'template_page_edit.html', {
        'customer': customer,
        'today_date': date.today().strftime('%d-%m-%Y'),
        'all_data': all_data,  # Dict: thickness -> list of Measurement objects
        'extra_charges': extra_charges,
    })
