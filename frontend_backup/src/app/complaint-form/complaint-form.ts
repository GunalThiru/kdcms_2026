import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NgForm } from '@angular/forms';
import { FormsModule } from '@angular/forms';

import { ComplaintService } from '../services/complaint-service';
import { ReportingStaff, ReportingStaffService } from '../services/reporting-staff';
import { AuthService } from '../services/auth';

@Component({
  selector: 'app-complaint-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './complaint-form.html',
  styleUrls: ['./complaint-form.css']
})
export class ComplaintFormComponent implements OnInit {

  // -------------------------------
  // ROLE / USER
  // -------------------------------
  userId: number | null = null;
  complaint_no: string = '';
  userRole = '';
  isStaff = false;
  isCustomer = false;
  isGuest = false;

  allowedfileTypes = [
    'Image', 'Video', 'Audio',
    'PDF', 
    'Text File'
  ];

  // -------------------------------
  // FORM DATA
  // -------------------------------
  formData: any = {
    problem_type: '',
    sub_problem_type: '',
    problem_description: '',

    date_of_issue: '',
    reporting_time: '',
    reporting_mode: '',

    solution_provided: '',
    solution_date_time: '',
    remarks: '',

    reference_type: '',
    reference_id: '',
    reporter_name: '',  // <-- for guest
    guest_mobile: '',
    guest_email: '',

    reported_by: null,
    resolved_by: null
    
  };

  // -------------------------------
  // LOOKUPS
  // -------------------------------
  problemSubProblemMap: any = {};
  problemTypes: string[] = [];
  subProblemTypes: string[] = [];
  reportingStaff: ReportingStaff[] = [];

  // -------------------------------
  // FILES
  // -------------------------------
  attachments: any[] = [];
  selectedFiles: any[] = [];

  // -------------------------------
  // UI
  // -------------------------------
  showSubProblemError = false;
  successMessage = '';
  errorMessage = '';
  initByRole = this.initFormByRole.bind(this);

  @ViewChild('fileInput') fileInput!: ElementRef;

  constructor(
    private complaintService: ComplaintService,
    private reportingStaffService: ReportingStaffService,
    private authService: AuthService
  ) {}

  // ===============================
  // INIT
  // ===============================
  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => {
      if (!user) {
        this.isStaff = false;
        this.isCustomer = false;
        this.isGuest = true; // treat as guest
      } else {
        this.userRole = user.role;
        this.userId = user.id;

        this.isStaff = ['staff', 'admin', 'sub_admin'].includes(user.role);
        this.isCustomer = user.role === 'customer';
        this.isGuest = false;
      }

      this.initByRole();
      this.loadProblemMap();
    });
  }

  // ===============================
  // USER / ROLE
  // ===============================
  private initFormByRole(): void {
    const ist = this.getCurrentISTDateTime();

    if (this.isCustomer) {
      this.formData.date_of_issue = ist.slice(0, 10);
      this.formData.reporting_time = ist.slice(11, 16);
      this.formData.reporting_mode = 'app';
      this.formData.reported_by = this.userId;

      this.formData.solution_provided = '';
      this.formData.solution_date_time = '';
      this.formData.remarks = '';
      this.formData.resolved_by = null;
    }

    if (this.isStaff) {
      // this.formData.resolved_by = this.userId;
      this.formData.guest_mobile = '';
      this.formData.guest_email = '';
      this.formData.solution_date_time = ist;

      this.reportingStaffService.getReportingStaff().subscribe({
        next: data => this.reportingStaff = data,
        error: err => console.error(err)
      });
    }

    if (this.isGuest) {
      this.formData.date_of_issue = ist.slice(0, 10);
      this.formData.reporting_time = ist.slice(11, 16);
      this.formData.reporting_mode = 'app';
      this.formData.reported_by = null;
      this.formData.reporter_name = '';
      this.formData.reference_type = '';
      this.formData.reference_id = '';
      this.formData.guest_mobile = '';
      this.formData.guest_email = '';
      
    }
  }

  private loadProblemMap(): void {
    this.complaintService.getProblemSubProblemMap().subscribe({
      next: map => {
        this.problemSubProblemMap = map;
        this.problemTypes = Object.keys(map);
      }
    });
  }

  // ===============================
  // LOAD EXISTING COMPLAINT
  // ===============================
  loadComplaint(complaint: any): void {
    this.formData = { ...complaint };
    this.formData.id = complaint.id;
    this.formData.complaint_no = complaint.complaint_no;

    this.attachments = [];
    this.selectedFiles = [];
    this.clearMessages();

    if (this.isStaff) {
      // this.formData.resolved_by = this.userId;
      this.formData.solution_date_time = this.getCurrentISTDateTime();
    }
  }

  // ===============================
  // HELPERS
  // ===============================
  getCurrentISTDateTime(): string {
    const now = new Date();
    const ist = now.toLocaleString('en-GB', {
      timeZone: 'Asia/Kolkata',
      hour12: false
    });
    const [d, t] = ist.split(', ');
    const [day, month, year] = d.split('/');
    const [h, m, s] = t.split(':');
    return `${year}-${month}-${day} ${h}:${m}:${s}`;
  }

  onProblemTypeChange(): void {
    this.subProblemTypes =
      this.problemSubProblemMap[this.formData.problem_type] || [];
    this.formData.sub_problem_type = '';
  }

  checkSubProblemClick(): void {
    if (!this.formData.problem_type) {
      this.showSubProblemError = true;
      setTimeout(() => (this.showSubProblemError = false), 2000);
    }
  }

  // ===============================
  // FILES
  // ===============================
  onFileChange(event: any): void {
    const files: FileList = event.target.files;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      if (this.attachments.find(f => f.raw.name === file.name)) continue;

      const type = this.getFileCategory(file.type, file.name);
      //  Block disallowed file types
    if (!this.allowedfileTypes.includes(type)) {
      this.showError(`File type "${type}" is not allowed`);
      continue;
    }

    // Prevent duplicates
    if (this.attachments.find(f => f.raw.name === file.name)) continue;


      this.selectedFiles.push({
        name: file.name,
        type,
        size: (file.size / 1024).toFixed(2)
      });

      this.attachments.push({
        raw: file,
        file_type: type,
        size: file.size
      });
    }

    event.target.value = '';
  }

  getFileCategory(mime: string, filename: string): string {
    if (mime.startsWith('image')) return 'Image';
    if (mime.startsWith('video')) return 'Video';
    if (mime.startsWith('audio')) return 'Audio';

    const ext = filename.split('.').pop()?.toLowerCase() || '';
    if (['pdf'].includes(ext)) return 'PDF';
    if (['doc', 'docx'].includes(ext)) return 'Word Document';
    if (['xls', 'xlsx', 'csv'].includes(ext)) return 'Excel';
    if (['txt'].includes(ext)) return 'Text File';

    return 'Other File';
  }

  getIconForFile(fileName: string): string {
    const ext = fileName.split('.').pop()?.toLowerCase() || '';
    const icons: any = {
      png: '/icons/image.png',
      jpg: '/icons/image.png',
      jpeg: '/icons/image.png',
      pdf: '/icons/pdf.png',
      // xls: '/icons/excel.png',
      // xlsx: '/icons/excel.png',
      // csv: '/icons/excel.png',
      // doc: '/icons/word.png',
      // docx: '/icons/word.png',
      txt: '/icons/txt.png',
      mp4: '/icons/video.png',
      mov: '/icons/video.png',
      mp3: '/icons/audio.png',
      wav: '/icons/audio.png',
      // zip: '/icons/zip-file.png',
      // rar: '/icons/zip-file.png'
    };
    return icons[ext] || '/icons/files.png';
  }

  // ===============================
  // SAVE / RESOLVE
  // ===============================
 saveComplaint(resolve: boolean) {

  // Validate required fields for guest complaints
  if (!this.formData.reported_by) {
    if (!this.formData.guest_mobile || this.formData.guest_mobile.length !== 10) {
      this.showError('Valid mobile number is required');
      return;
    }
    if (!this.formData.guest_email) {
      this.showError('Email is required');
      return;
    }
  }

  if (!this.formData.problem_type) {
    this.showError('Problem type is required');
    return;
  }
  if (!this.formData.sub_problem_type) {
    this.showError('Sub-problem type is required');
    return;
  }

  if (!this.formData.id) {
    // CREATE complaint (guest/customer submission)
    const data = new FormData();
    Object.keys(this.formData).forEach(key => {
      const val = this.formData[key];
      if (val !== null && val !== '') data.append(key, val);
    });
    this.attachments.forEach(f => data.append('attachments', f.raw));

    this.complaintService.createComplaint(data).subscribe({
      next: (res: any) => {
        this.formData.id = res.id;
        this.complaint_no = res.complaint_no;
        this.showSuccess(`Complaint created successfully. Complaint No: ${this.complaint_no}`);
        this.saveComplaint(resolve); // recursive call
      },
      error: (err: any) => this.showError('Failed to create complaint')
    });
    return;
  }

  // VALIDATION AGAIN for **existing complaint**
  if (!this.formData.reported_by) {
    // guest complaint, mobile/email must exist
    if (!this.formData.guest_mobile || this.formData.guest_mobile.length !== 10) {
      this.showError('Valid mobile number is required');
      return;
    }
    if (!this.formData.guest_email) {
      this.showError('Email is required');
      return;
    }
  }

  // Now proceed to resolve/save
  if (resolve) {
    if (!this.formData.solution_provided) {
      this.showError('Please provide a solution before resolving');
      return;
    }
    this.complaintService
      .resolveComplaint(this.formData.id, this.formData.solution_provided, this.userId!)
      .subscribe({
        next: () => this.showSuccess(`Complaint ${this.complaint_no} resolved successfully`),
        error: () => this.showError('Failed to resolve complaint')
      });
  } else {
    this.complaintService
      .saveStaffAction(this.formData.id, this.formData.solution_provided, this.formData.remarks)
      .subscribe({
        next: () => this.showSuccess(`Complaint ${this.complaint_no ?? ''} saved as in-progress`),
        error: () => this.showError('Failed to save complaint')
      });
  }
}

sendMail(): void {
  if (!this.formData.id) {
    this.showError('Complaint must be saved before sending mail');
    return;
  }

  this.complaintService.sendComplaintMail(this.formData.id).subscribe({
    next: () => {
      this.showSuccess('Mail sent successfully');
    },
    error: (err) => {
      console.error(err);
      this.showError('Failed to send mail');
    }
  });
}



  // ===============================
  // SUBMIT (CUSTOMER / GUEST)
  // ===============================
  onSubmit(form: NgForm): void {
if (!this.formData.problem_type) {
  this.showError('Problem type is required');
  return;
}
if (!this.formData.sub_problem_type) {
  this.showError('Sub-problem type is required');
  return;
}

    if (!this.formData.guest_mobile || this.formData.guest_mobile.length !== 10) {
  this.showError('Valid mobile number is required');
  return;
}

if (!this.formData.guest_email) {
  this.showError('Email is required');
  return;
}

    if (form.invalid) {
      this.showError('Please fill all required fields') ;
      return;
    }

    const data = new FormData();
    Object.keys(this.formData).forEach(key => {
      const val = this.formData[key];
      if (val !== null && val !== '') data.append(key, val);
    });

    this.attachments.forEach(f => {
      data.append('attachments', f.raw);
      data.append('file_types', f.file_type);
      data.append('file_sizes', f.size.toString());
    });

    this.complaintService.createComplaint(data).subscribe({
      next: (res: any) => {
        this.formData.id = res.id;
        this.showSuccess(`Complaint submitted! complaint_no: ${res.complaint_no}`);
        this.errorMessage = '';
        form.resetForm();
        this.attachments = [];
        this.selectedFiles = [];
        this.fileInput.nativeElement.value = '';
      },
      error: (err: any) => {
        this.showError('Failed to submit complaint');
        console.error(err);
      }
    });
  }

  removeFile(index: number): void {
    this.attachments.splice(index, 1);
    this.selectedFiles.splice(index, 1);
  }

  clearMessages(): void {
    this.successMessage = '';
    this.errorMessage = '';
  }


 showSuccess(message: string): void {
  this.successMessage = message;
  this.errorMessage = ''; // clear errors
  // optional auto-hide
  setTimeout(() => {
    this.successMessage = '';
  }, 5000); // hides after 5 seconds
}

showError(message: string): void {
  this.errorMessage = message;
  this.successMessage = ''; // clear success
  setTimeout(() => {
    this.errorMessage = '';
  }, 5000);
}


}
