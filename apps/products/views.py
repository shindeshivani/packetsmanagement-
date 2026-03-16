from django.shortcuts import render,redirect
from .models import PacketEntry
from datetime import datetime
from django.contrib import messages
from django.db.models import Sum
from django.db.models.functions import TruncMonth 
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required

# Create your views here.
#login view
def login_page(request):

    if request.user.is_authenticated:
        return redirect("entry_page")

    if request.method=="POST":

        username=request.POST.get("username")
        password=request.POST.get("password")

        user=authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            return redirect("entry_page")
        
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")
      
    return render(request,"login.html")

def logout_view(request):
    logout(request)
    return redirect('login')


#make entry view
@login_required
def entry_page(request):

    if request.method=='POST':

        packet_one_kg=request.POST.get("packet_one_kg")
        packet_half_kg=request.POST.get("packet_half_kg")
        price_one_kg=request.POST.get("price_one_kg")
        price_half_kg=request.POST.get('price_half_kg')


        # check if any field empty
        if  packet_one_kg=="" or packet_half_kg=="" or price_one_kg=="" or price_half_kg=="":
            return render(request,'entry.html',{'error':"Please enter all values"})


        packet_one_kg=int(packet_one_kg)
        packet_half_kg=int(packet_half_kg)
        price_one_kg=int(price_one_kg)
        price_half_kg=int(price_half_kg)

        if all(v == 0 for v in [packet_one_kg, packet_half_kg, price_one_kg, price_half_kg]):
            return render(request,'entry.html',{'error':"Please enter at least one non-zero value"})

        PacketEntry.objects.create(
            packet_one_kg=packet_one_kg,
            packet_half_kg=packet_half_kg,
            price_one_kg=price_one_kg*packet_one_kg,
            price_half_kg=price_half_kg *packet_half_kg           
        )
        
        messages.success(request,"Entry saved successfully!")
        return redirect("entry_page")
    
    return render(request,'entry.html')

#Date-report view
@login_required
def date_report(request):
    
    records=None
    start_date=None
    end_date=None

    if request.method=='POST':
        start_date=request.POST.get("start_date")
        end_date=request.POST.get("end_date")

        # check if dates are missing
        if not start_date or not end_date:
            messages.error(request, "Please select both start and end dates")

        # check date logic
        elif start_date > end_date:
            messages.error(request, "Start date cannot be greater than end date")

        else:
            records = PacketEntry.objects.filter(
                created_at__date__range=[start_date, end_date]
            )

            if not records.exists():
                messages.error(request, "No records found for selected dates")

    context={
        "records":records,
        "start_date":start_date,
        "end_date":end_date,
        }    

    return render(request,'date_report.html',context)    

#month report
@login_required
def monthly_report(request):
    
    data=(
        PacketEntry.objects.annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(
            total_one_kg=Sum('packet_one_kg'),
            total_half_kg=Sum('packet_half_kg'),
            total_price_one_kg=Sum('price_one_kg'),
            total_price_half_kg=Sum('price_half_kg')
        )
        .order_by('month')
    )
    #calculate overall total
    for row in data:
        row['overall_total']=row['total_price_one_kg']+row['total_price_half_kg']

    return render(request,'monthly_report.html',{'data':data})    


#Manage records
@login_required
def manage_records(request):

    records = None
    start_date = None
    end_date = None
    

    if request.method=="POST":
        start_date=request.POST.get("start_date")
        end_date=request.POST.get("end_date")

        if not start_date or not end_date:
            messages.error(request,"Please select both start and end dates")
            return redirect("manage_records")
        
        if start_date > end_date:
            messages.error(request, "Start date cannot be greater than end date")
            return redirect("manage_records") 

        records=PacketEntry.objects.filter(
            created_at__date__range=[start_date,end_date]
            ).order_by('-created_at')

        if not records:
            messages.error(request,"No records found for selected dates")

    
        return render(request,"manage_records.html",{
            "records": records,
            "start_date":start_date,
            "end_date":end_date
            })

    return render(request, "manage_records.html")


#edit view
@login_required
def edit_record(request, id):


    record = PacketEntry.objects.get(id=id)
    

    if request.method == "POST":

        packet_one_kg = request.POST.get("packet_one_kg")
        packet_half_kg = request.POST.get("packet_half_kg")
        price_one_kg = request.POST.get("price_one_kg")
        price_half_kg = request.POST.get("price_half_kg")
        

        # empty check
        if packet_one_kg == "" or packet_half_kg == "" or price_one_kg == "" or price_half_kg == "":
            return render(request, "edit_records.html", {
                "record": record,
                "error": "Please enter all values"
            })

        # convert to int
        packet_one_kg = int(packet_one_kg)
        packet_half_kg = int(packet_half_kg)
        price_one_kg = int(price_one_kg)
        price_half_kg = int(price_half_kg)
        

        record.packet_one_kg = packet_one_kg
        record.packet_half_kg = packet_half_kg
        record.price_one_kg = price_one_kg 
        record.price_half_kg = price_half_kg 
       
        record.save()

        messages.success(request, "Record updated successfully")

        return redirect("manage_records")

    return render(request, "edit_records.html", {"record": record})

#delete_view
@login_required
def delete_record(request, id):


    record = PacketEntry.objects.get(id=id)
    record.delete()

    messages.success(request, "Record deleted successfully")

    return redirect("manage_records")

