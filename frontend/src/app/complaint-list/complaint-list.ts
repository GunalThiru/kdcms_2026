import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { ComplaintService } from '../services/complaint-service';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../services/auth';


@Component({
  standalone: true,
  selector: 'app-complaints-list',
  imports: [CommonModule, FormsModule],
  templateUrl: './complaint-list.html',
  styleUrls: ['./complaint-list.css']
})
export class ComplaintList implements OnInit {

  //paggination params

pageSizes = [5,10, 25, 50, 100]; // hard coded


//initial values
pageSize = 10;
currentPage = 1;
totalRecords = 0;
totalPages = 1;


  complaints: any[] = [];
  loading = false;
  problemMap: any = {};
problemTypes: string[] = [];
subProblemTypes: string[] = [];







  // filters
  filters: {
  status?: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED';
  problem_type?: string;
  sub_problem_type?: string;
  from_date?: string;
  to_date?: string;
  search?: string;
} = {};


  constructor(
    private complaintService: ComplaintService,
    private route: ActivatedRoute,
    private http: HttpClient ,
    private authService: AuthService
  ) {}

  ngOnInit(): void {

    this.loadProblemMap();

    // 1️⃣ Read status from URL and load complaints
    this.route.queryParams.subscribe(params => {
      if (params['status']) {
        this.filters.status = params['status'] as
          'PENDING' | 'IN_PROGRESS' | 'COMPLETED';
      } else {
        // Clear status if no param provided
        delete this.filters.status;
      }
      this.currentPage = 1; // Reset to first page when filters change
      this.loadComplaints();
    });
  }

  // 2️⃣ Load complaints with filters
loadComplaints() {
  this.loading = true;

  const filtersToSend = { ...this.filters };

  // validate status
  if (
    filtersToSend.status &&
    !['PENDING', 'IN_PROGRESS', 'COMPLETED'].includes(filtersToSend.status)
  ) {
    delete filtersToSend.status;
  }

  this.complaintService.getComplaints(
    filtersToSend,
    this.currentPage,
    this.pageSize
  ).subscribe({
    next: (res) => {
      // Initialize expandable text properties for each complaint
      this.complaints = res.data.map((complaint: any) => ({
        ...complaint,
        descExpanded: false,
        solutionExpanded: false
      }));
      this.totalRecords = res.total;       // 👈 IMPORTANT
      this.totalPages = Math.ceil(
        this.totalRecords / this.pageSize
      );
      this.loading = false;
    },
    error: () => {
      this.loading = false;
      alert('Failed to load complaints');
    }
  });
}


  // 3️⃣ Apply filters button
  applyFilters() {
    this.loadComplaints();
  }

  // 4️⃣ Reset filters
  resetFilters() {
  this.filters = {};
  this.loadComplaints();
}
loadProblemMap() {
  this.http.get<any>('problem_sub_problem_map.json') // just the file name in public
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
    this.subProblemTypes =
      this.problemMap[this.filters.problem_type] || [];
  } else {
    this.subProblemTypes = [];
  }

  this.filters.sub_problem_type = undefined;
  this.loadComplaints();
}


navigateByStatus(status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED') {
  if (status === 'IN_PROGRESS' || status === 'PENDING') {
    window.location.href = '/tasks'; // Or use Angular Router
  } else if (status === 'COMPLETED') {
    window.location.href = '/complaints-list?status=COMPLETED';
  }
}

changePage(page: number) {
  if (page < 1 || page > this.totalPages) return;
  this.currentPage = page;
  this.loadComplaints();
}

onPageSizeChange() {
  this.currentPage = 1; // reset to first page
  this.loadComplaints();
}



}
