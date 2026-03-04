from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vehicle, ServiceLog
from .forms import VehicleForm, ServiceLogForm

@login_required
def vehicle_list(request):
    vehicles = Vehicle.objects.all()
    return render(request, 'vehicles/vehicle_list.html', {'vehicles': vehicles})

@login_required
def vehicle_create(request):
    form = VehicleForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Vehicle added.')
        return redirect('vehicle_list')
    return render(request, 'vehicles/vehicle_form.html', {'form': form, 'title': 'Add Vehicle'})

@login_required
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    logs = ServiceLog.objects.filter(vehicle=vehicle)
    return render(request, 'vehicles/vehicle_detail.html', {'vehicle': vehicle, 'logs': logs})

@login_required
def vehicle_edit(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    form = VehicleForm(request.POST or None, request.FILES or None, instance=vehicle)
    if form.is_valid():
        form.save()
        messages.success(request, 'Vehicle updated.')
        return redirect('vehicle_detail', pk=pk)
    return render(request, 'vehicles/vehicle_form.html', {'form': form, 'title': 'Edit Vehicle'})

@login_required
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, 'Vehicle deleted.')
        return redirect('vehicle_list')
    return render(request, 'confirm_delete.html', {'obj': vehicle, 'cancel_url': 'vehicle_list'})

@login_required
def service_add(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    form = ServiceLogForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        log = form.save(commit=False)
        log.vehicle = vehicle
        log.save()
        # Update vehicle odometer if provided
        if log.odometer_at_service and (not vehicle.odometer or log.odometer_at_service > vehicle.odometer):
            vehicle.odometer = log.odometer_at_service
            vehicle.save()
        messages.success(request, 'Service log added.')
        return redirect('vehicle_detail', pk=pk)
    return render(request, 'vehicles/service_form.html', {'form': form, 'vehicle': vehicle})

@login_required
def service_delete(request, pk):
    log = get_object_or_404(ServiceLog, pk=pk)
    vehicle_pk = log.vehicle_id
    if request.method == 'POST':
        log.delete()
        messages.success(request, 'Service log deleted.')
    return redirect('vehicle_detail', pk=vehicle_pk)
