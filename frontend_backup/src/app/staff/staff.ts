import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ComplaintFormComponent } from '../complaint-form/complaint-form';
import { ReportingStaffService } from '../services/reporting-staff';
import { ReportingStaff } from '../services/reporting-staff';

@Component({
  selector: 'app-staff',
  standalone: true,   // ✅ REQUIRED
  imports: [CommonModule, ComplaintFormComponent],
  templateUrl: './staff.html',
  styleUrl: './staff.css',
})
export class Staff implements OnInit {

  reportingStaff: ReportingStaff[] = [];
  complaint = { reported_by: null };

  // ✅ Inject SERVICE (not array)
  constructor(
    private reportingStaffService: ReportingStaffService
  ) {}

  ngOnInit() {
    this.reportingStaffService.getReportingStaff().subscribe(
      (data: ReportingStaff[]) => {
        this.reportingStaff = data;
      }
    );
  }

   sidebarCollapsed = false;

  toggleSidebar() {
    this.sidebarCollapsed = !this.sidebarCollapsed;
  }
}
