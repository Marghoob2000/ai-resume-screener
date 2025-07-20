from django.db import models
from django.contrib.auth.models import User

class JobDescription(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Resume(models.Model):
    title = models.CharField(max_length=255)
    resume_file = models.FileField(upload_to='resumes/') # Stores the uploaded PDF
    extracted_text = models.TextField(blank=True, null=True) # Will store the parsed text
    job_description = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name='resumes')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title