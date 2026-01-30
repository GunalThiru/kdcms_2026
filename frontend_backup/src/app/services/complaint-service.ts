import { Injectable } from '@angular/core';
import { HttpClient,HttpParams,HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';


export interface Complaint {
  
  id: number;
  problem_description: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED';
}
export interface TaskAttachment {
  id: number;
  file_name: string;
  file_size: number;
  file_url: string;

  /* derived on frontend */
  icon?: string;
}

export interface Task {
  /* ================= BASIC ================= */
  id: number;

  complaint_no: string;

  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED';

  problem_description: string;

  created_at?: string;

  /* ================= PROBLEM INFO ================= */
  problem_type?: string | null;
  sub_problem_type?: string | null;

  /* ================= REPORTER INFO ================= */
  reported_by?: string | null;       // STAFF / GUEST / etc
  reporter_name?: string | null;     // used when GUEST

  /* ================= VIEW TRACKING ================= */
  last_viewed_at?: string | null;
  last_viewed_by?: string | null;

  /* ================= ATTACHMENTS ================= */
  attachments?: TaskAttachment[];

  /* ================= SOLUTION ================= */
  solution_provided?: string | null;
}




@Injectable({
  providedIn: 'root'
})
export class ComplaintService {

  private baseUrl = 'http://localhost:5000/complaints';
  private taskUrl = 'http://localhost:5000/tasks';


  private getAuthHeaders(): HttpHeaders {
  const token = localStorage.getItem('access_token');
  return new HttpHeaders({
    Authorization: `Bearer ${token}`
  });
}


  constructor(private http: HttpClient) {}

  // ===============================
  // CREATE COMPLAINT (Customer + Staff Save)
  // ===============================
  createComplaint(formData: FormData): Observable<any> {
    return this.http.post(this.baseUrl, formData);
  }

  // ===============================
  // SAVE AS TASK (Staff - In Progress)
  // ===============================
  saveAsTask(formData: FormData): Observable<any> {
    return this.http.post(`${this.baseUrl}`, formData);
  }

  // ===============================
  // RESOLVE COMPLAINT (Staff)
  // ===============================
resolveComplaint(complaintId: number, solution: string, resolvedBy: number) {
  return this.http.put(`${this.baseUrl}/${complaintId}/resolve`, {
    solution_provided: solution,
    resolved_by: resolvedBy
  });
}


  // ===============================
  // PROBLEM / SUB-PROBLEM MAP
  // ===============================
  getProblemSubProblemMap(): Observable<any> {
    return this.http.get('problem_sub_problem_map.json');
  }

  // ===============================
  // TASKS
  // ===============================
getTasks(filters?: any, page: number = 1, pageSize: number = 10): Observable<any> {
  let params = new HttpParams()
    .set('page', page.toString())
    .set('pageSize', pageSize.toString());

  if (filters) {
    if (filters.status) params = params.set('status', filters.status);
    if (filters.problem_type) params = params.set('problem_type', filters.problem_type);
    if (filters.sub_problem_type) params = params.set('sub_problem_type', filters.sub_problem_type);
    if (filters.from_date) params = params.set('from_date', filters.from_date);
    if (filters.to_date) params = params.set('to_date', filters.to_date);
    if (filters.search) params = params.set('search', filters.search);
  }

  return this.http.get<any>(`${this.taskUrl}`, { params });
}



  getOpenTaskCount(): Observable<{ open_tasks: number }> {
    return this.http.get<{ open_tasks: number }>(
      'http://localhost:5000/tasks/count'
    );
  }

  saveStaffAction(complaintId: number, solution: string, remarks: string) {
  return this.http.put(`${this.baseUrl}/${complaintId}/staff-action`, {
    solution_provided: solution,
    remarks: remarks
  });
}

markInProgress(taskId: number) {
  return this.http.post(
    `${this.baseUrl}/${taskId}/in-progress`,
    {}
  );
}

// ===============================
// TASK VIEW TRACKING
// ===============================
markTaskViewed(taskId: number): Observable<any> {
  return this.http.post(
    `${this.taskUrl}/${taskId}/view`,
    null,
    { headers: this.getAuthHeaders() }
  );
}



// ----------------------------------
  // GET COMPLAINTS WITH FILTERS
  // ----------------------------------
getComplaints(
  filters?: {
    status?: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED';
    problem_type?: string;
    sub_problem_type?: string;
    from_date?: string;
    to_date?: string;
    search?: string;
  },
  page: number = 1,
  pageSize: number = 10
): Observable<{
  data: any[];
  total: number;
  page: number;
  page_size: number;
}> {

  let params = new HttpParams()
    .set('page', page)
    .set('page_size', pageSize);

  if (filters) {
    Object.keys(filters).forEach((key) => {
      const value = (filters as any)[key];
      if (value !== null && value !== undefined && value !== '') {
        params = params.set(key, value);
      }
    });
  }

  return this.http.get<{
    data: any[];
    total: number;
    page: number;
    page_size: number;
  }>(`${this.baseUrl}/list`, { params });
}


  // ----------------------------------
  // DASHBOARD SUMMARY
  // (OPTIONAL – will wire later)
  // ----------------------------------
  getSummary(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/summary`);
  }


  sendComplaintMail(complaintId: number) {
  return this.http.post(
    `${this.baseUrl}/${complaintId}/send-mail`,
    {}
  );
}



}
