import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ComplaintService } from '../services/complaint-service';

@Component({
  standalone: true,
  selector: 'app-complaints-report',
  imports: [CommonModule],
  templateUrl: './complaint-report.html',
  styleUrls: ['./complaint-report.css']
})
export class ComplaintReport implements OnInit {

  summary = {
    total: 0,
    pending: 0,
    in_progress: 0,
    completed: 0
  };

  constructor(
    private complaintService: ComplaintService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadSummary();
  }

  loadSummary() {
    this.complaintService.getSummary().subscribe(res => {
      this.summary = res;
    });
  }

  openList(status: string) {
    this.router.navigate(['/complaints-list'], {
      queryParams: { status }
    });
  }


  openTasks() {
    this.router.navigate(['/tasks']);
  } 
}
