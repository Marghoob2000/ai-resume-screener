# core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import JobDescription, Resume
from .forms import JobDescriptionForm, ResumeUploadForm
from .matcher import get_ranked_resumes
import pdfplumber

def job_list(request):
    """
    Handles the display of all job descriptions and the creation of a new one.
    """
    # Handles the form submission for creating a new job description
    if request.method == 'POST':
        form = JobDescriptionForm(request.POST)
        if form.is_valid():
            # Associate the job with the logged-in user before saving
            # Note: Assumes the user is logged in. You might want to add @login_required decorator.
            job_description = form.save(commit=False)
            job_description.created_by = request.user
            job_description.save()
            return redirect('job_list')
    else:
        form = JobDescriptionForm()
    
    # Fetches all job objects from the database to display in the list
    jobs = JobDescription.objects.all()
    
    # Renders the template with the list of jobs and the form
    return render(request, 'core/job_list.html', {'jobs': jobs, 'form': form})

def job_detail(request, pk):
    """
    Handles the detail view for a single job, resume uploads, and displaying ranked results.
    """
    # Get the specific JobDescription object or return a 404 error if not found
    job = get_object_or_404(JobDescription, pk=pk)
    
    # Handles the form submission for uploading a new resume
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.job_description = job
            resume.save() # Save the resume instance first to get a file path

            # Parse the newly uploaded PDF and save its text content
            try:
                with pdfplumber.open(resume.resume_file.path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        # Add 'or ""' to handle pages that might not have extractable text
                        text += page.extract_text() or ""
                    resume.extracted_text = text
                    resume.save() # Save the instance again with the extracted text
            except Exception as e:
                # Basic error handling for PDF parsing
                print(f"Error parsing PDF {resume.resume_file.path}: {e}")
                resume.extracted_text = "Error: Could not parse PDF."
                resume.save()

            # Redirect back to the same page to show the updated list
            return redirect('job_detail', pk=job.pk)
    else:
        # If it's a GET request, just create an empty form
        form = ResumeUploadForm()

    # Get all resumes associated with this job
    all_resumes = Resume.objects.filter(job_description=job)
    
    # Call the AI matching function from matcher.py
    # This will return a list of (resume, score) tuples, ranked by relevance
    ranked_resumes = get_ranked_resumes(job.text, all_resumes)
    
    # Prepare the context dictionary to pass to the template
    context = {
        'job': job, 
        'ranked_resumes': ranked_resumes, 
        'form': form
    }
    
    # Renders the detail page with the job info, ranked results, and upload form
    return render(request, 'core/job_detail.html', context)