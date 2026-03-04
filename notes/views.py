import markdown as md
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.safestring import mark_safe
from .models import Note, NoteCategory
from .forms import NoteForm

# Markdown extensions for full-featured rendering
MD_EXTENSIONS = [
    'markdown.extensions.tables',       # GFM-style tables
    'markdown.extensions.fenced_code',  # ```code blocks```
    'markdown.extensions.nl2br',        # newline → <br>
    'markdown.extensions.toc',          # [TOC] auto table of contents
    'markdown.extensions.sane_lists',   # better list handling
    'markdown.extensions.smarty',       # smart quotes / dashes
]


def render_markdown(text):
    """Convert markdown text to safe HTML."""
    html = md.markdown(text, extensions=MD_EXTENSIONS)
    return mark_safe(html)


@login_required
def note_list(request):
    tag = request.GET.get('tag', '')
    category = request.GET.get('category', '')
    notes = Note.objects.all()
    if tag:
        notes = notes.filter(tags__icontains=tag)
    if category:
        notes = notes.filter(category__name=category)
    categories = NoteCategory.objects.all()
    return render(request, 'notes/note_list.html', {
        'notes': notes,
        'categories': categories,
        'tag': tag,
        'selected_category': category,
    })


@login_required
def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk)
    body_html = render_markdown(note.body)
    return render(request, 'notes/note_detail.html', {
        'note': note,
        'body_html': body_html,
    })


@login_required
def note_create(request):
    form = NoteForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Note created.')
        return redirect('note_list')
    return render(request, 'notes/note_form.html', {'form': form, 'title': 'New Note'})


@login_required
def note_edit(request, pk):
    note = get_object_or_404(Note, pk=pk)
    form = NoteForm(request.POST or None, instance=note)
    if form.is_valid():
        form.save()
        messages.success(request, 'Note updated.')
        return redirect('note_detail', pk=pk)
    return render(request, 'notes/note_form.html', {'form': form, 'title': 'Edit Note'})


@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted.')
        return redirect('note_list')
    return render(request, 'confirm_delete.html', {'obj': note, 'cancel_url': 'note_list'})
