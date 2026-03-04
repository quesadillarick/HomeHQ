from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Asset, InsurancePolicy
from .forms import AssetForm, InsurancePolicyForm

@login_required
def asset_list(request):
    category = request.GET.get('category', '')
    assets = Asset.objects.all()
    if category:
        assets = assets.filter(category=category)
    total = sum(a.value for a in assets)
    return render(request, 'assets/asset_list.html', {'assets': assets, 'total': total, 'category': category})

@login_required
def asset_create(request):
    form = AssetForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Asset added.')
        return redirect('asset_list')
    return render(request, 'assets/asset_form.html', {'form': form, 'title': 'Add Asset'})

@login_required
def asset_edit(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    form = AssetForm(request.POST or None, request.FILES or None, instance=asset)
    if form.is_valid():
        form.save()
        messages.success(request, 'Asset updated.')
        return redirect('asset_list')
    return render(request, 'assets/asset_form.html', {'form': form, 'title': 'Edit Asset'})

@login_required
def asset_delete(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        asset.delete()
        messages.success(request, 'Asset deleted.')
        return redirect('asset_list')
    return render(request, 'confirm_delete.html', {'obj': asset, 'cancel_url': 'asset_list'})

@login_required
def loss_report(request):
    assets = Asset.objects.all().order_by('category')
    total = sum(a.value for a in assets)
    by_category = {}
    for a in assets:
        cat = a.get_category_display()
        if cat not in by_category:
            by_category[cat] = {'items': [], 'total': 0}
        by_category[cat]['items'].append(a)
        by_category[cat]['total'] += a.value
    return render(request, 'assets/loss_report.html', {'by_category': by_category, 'total': total})

@login_required
def insurance_list(request):
    policies = InsurancePolicy.objects.all()
    return render(request, 'assets/insurance_list.html', {'policies': policies})

@login_required
def insurance_create(request):
    form = InsurancePolicyForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Policy added.')
        return redirect('insurance_list')
    return render(request, 'assets/insurance_form.html', {'form': form, 'title': 'Add Policy'})

@login_required
def insurance_edit(request, pk):
    policy = get_object_or_404(InsurancePolicy, pk=pk)
    form = InsurancePolicyForm(request.POST or None, instance=policy)
    if form.is_valid():
        form.save()
        messages.success(request, 'Policy updated.')
        return redirect('insurance_list')
    return render(request, 'assets/insurance_form.html', {'form': form, 'title': 'Edit Policy'})

@login_required
def insurance_delete(request, pk):
    policy = get_object_or_404(InsurancePolicy, pk=pk)
    if request.method == 'POST':
        policy.delete()
        messages.success(request, 'Policy deleted.')
        return redirect('insurance_list')
    return render(request, 'confirm_delete.html', {'obj': policy, 'cancel_url': 'insurance_list'})
