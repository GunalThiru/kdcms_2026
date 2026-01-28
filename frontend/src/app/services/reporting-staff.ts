import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ReportingStaff {
  user_id: number;
  name: string;
}

@Injectable({
  providedIn: 'root'

  
})
export class ReportingStaffService {

  private baseUrl = 'http://localhost:5000/reporting-staff';

  

  constructor(private http: HttpClient) {}

  getReportingStaff(): Observable<ReportingStaff[]> {
    return this.http.get<ReportingStaff[]>(this.baseUrl);
  }
}
