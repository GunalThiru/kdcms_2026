import { Component, OnInit } from '@angular/core';
import { ComplaintService,Task } from '../../services/complaint-service';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth';
import { HttpClient } from '@angular/common/http';

@Component({
  standalone: true,
  selector: 'app-tasks',
  templateUrl: './tasks.html',
  styleUrls: ['./tasks.css'],
  imports: [CommonModule,RouterModule,FormsModule]
})
export class TasksComponent implements OnInit {
  

  // pagination params
  pageSizes = [5,10, 25, 50, 100]; // hard coded
  pageSize = 10;
  currentPage = 1;
  totalRecords = 0;
  totalPages = 1;

  tasks: Task[] = [];
  selectedTask: Task | null = null;

  loading = true;
  error = '';

  showModal = false;

  wasPendingOnOpen = false;

  // Filter properties
  filters: {
    status?: 'PENDING' | 'IN_PROGRESS';
    problem_type?: string;
    sub_problem_type?: string;
    from_date?: string;
    to_date?: string;
    search?: string;
  } = {};

  problemMap: any = {};
  problemTypes: string[] = [];
  subProblemTypes: string[] = [];

  constructor(
    private complaintService: ComplaintService, 
    private authService: AuthService,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.loadProblemMap();
    this.loadTasks();
  }

  loadProblemMap() {
    this.http.get<any>('problem_sub_problem_map.json')
      .subscribe({
        next: (map) => {
          this.problemMap = map;
          this.problemTypes = Object.keys(map);
        },
        error: (err) => {
          console.error('Failed to load problem map', err);
        }
      });
  }

  onProblemChange() {
    if (this.filters.problem_type) {
      this.subProblemTypes = this.problemMap[this.filters.problem_type] || [];
    } else {
      this.subProblemTypes = [];
    }
    this.filters.sub_problem_type = undefined;
    this.applyFilters();
  }

  applyFilters() {
    this.currentPage = 1;
    this.loadTasks();
  }

  resetFilters() {
    this.filters = {};
    this.subProblemTypes = [];
    this.currentPage = 1;
    this.loadTasks();
  }

  onPageSizeChange() {
    this.currentPage = 1;
    this.loadTasks();
  }

  changePage(page: number) {
    if (page < 1 || page > this.totalPages) return;
    this.currentPage = page;
    this.loadTasks();
  }

  loadTasks() {
    this.loading = true;
    
    const filtersToSend = { ...this.filters };

    // validate status
    if (
      filtersToSend.status &&
      !['PENDING', 'IN_PROGRESS'].includes(filtersToSend.status)
    ) {
      delete filtersToSend.status;
    }

    this.complaintService.getTasks(filtersToSend, this.currentPage, this.pageSize).subscribe({
      next: (res: any) => {
        console.log('TASK API RESPONSE:', res);
        // Handle both array response and paginated response
        if (Array.isArray(res)) {
          this.tasks = res;
          this.totalRecords = res.length;
          this.totalPages = 1;
        } else {
          this.tasks = res.data || res;
          this.totalRecords = res.total || this.tasks.length;
          this.totalPages = Math.ceil(this.totalRecords / this.pageSize);
        }
        this.loading = false;
      },
      error: () => {
        this.error = 'Failed to load tasks';
        this.loading = false;
      }
    });
  }

  getStatusLabel(status: string): string {
    if (status === 'PENDING') return 'New Complaint';
    if (status === 'IN_PROGRESS') return 'In Progress';
    return status;
  }
  
openTask(task: any) {
  this.selectedTask = { ...task };

  // Track initial status
  this.wasPendingOnOpen = task.status === 'PENDING';
  console.log("inside open()");


   // VIEW TRACKING
 this.selectedTask = { ...task };
  this.wasPendingOnOpen = task.status === 'PENDING';

  this.complaintService.markTaskViewed(task.id).subscribe({
    next: (res) => {
      console.log('View logged', res);
      // Update task in UI
      task.last_viewed_at = res.last_viewed_at;
      task.last_viewed_by = res.last_viewed_by;
      
    },
    error: (err) => console.error('View logging failed', err)
  });

  // Attach icons (unchanged)
  
  if (this.selectedTask?.attachments) {
  this.selectedTask.attachments = this.selectedTask.attachments.map(file => {
    const ext = file.file_name.split('.').pop()?.toLowerCase() || '';
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

    return { ...file, icon: icons[ext] || '/icons/files.png' };
  });
}


  this.showModal = true;
}


closeModal() {
  // 🔒 Capture values safely
  const taskId = this.selectedTask?.id;
  const shouldMarkInProgress = this.wasPendingOnOpen;

  if (taskId && shouldMarkInProgress) {
    this.complaintService.markInProgress(taskId).subscribe({
      next: () => {
        // Update UI list
        const taskInList = this.tasks.find(t => t.id === taskId);
        if (taskInList) {
          taskInList.status = 'IN_PROGRESS';`1`
        }
      },
      error: (err) => {
        console.error('Failed to mark complaint IN_PROGRESS', err);
      }
    });
  }

  // ✅ Close modal after API call
  this.showModal = false;
  this.selectedTask = null;
  this.wasPendingOnOpen = false;
}


  sendMail() {
    if (!this.selectedTask) return;

    this.complaintService.sendComplaintMail(this.selectedTask.id).subscribe({
      next: () => {
        alert('Email sent successfully!');
      },
      error: (err) => {
        console.error('Mail send error:', err);
        alert('Failed to send email. Please try again.');
      }
    });
  }

  resolveTask() {
    if (!this.selectedTask) return;

    if (!this.selectedTask.solution_provided || this.selectedTask.solution_provided.trim() === '') {
      alert('Please provide a solution before resolving.');
      return;
    }

    // TODO: Replace with actual logged-in staff ID
    const staffId = this.authService.getUserId();
    const staffName = this.authService.getUserName();

    console.log('Resolving task by staff:', staffId, staffName);
    if (!staffId || !staffName) {
      alert('You must be logged in to resolve a complaint.');
      return;
    }

    this.complaintService.resolveComplaint(
      this.selectedTask.id,
      this.selectedTask.solution_provided,
      staffId
    ).subscribe({
      next: () => {
        alert('Complaint resolved successfully!');
        this.closeModal();
        this.loadTasks(); // refresh task list
      },
      error: (err) => {
        console.error(err);
        alert('Failed to resolve complaint.');
      }
    });
  }

  getReporter(task: Task): string {
  if (task.reported_by) return task.reported_by;
  if (task.reporter_name) return `GUEST-${task.reporter_name}`;
  return 'N/A';
}


}
