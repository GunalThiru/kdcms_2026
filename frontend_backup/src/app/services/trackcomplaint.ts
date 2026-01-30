import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface TrackedComplaint {
  id: number;
  complaint_no: string;
  status: string;
  problem_type: string;
  sub_problem_type: string;
  reference_type: string;
  reference_id: string;
  problem_description: string;
  solution_provided?: string | null;
  created_at: string;
  remarks?: string | null;
}

@Injectable({ providedIn: 'root' })
export class ComplaintTrackingService {

  private baseUrl = 'http://localhost:5000';

  constructor(private http: HttpClient) {}

  /**
   * Guest + Logged-in complaint tracking
   * No JWT required
   */
  trackComplaint(
    complaint_no: string,
    referenceId: string
  ): Observable<TrackedComplaint> {

    return this.http.post<TrackedComplaint>(
      `${this.baseUrl}/complaints/track`,
      {
        complaint_no: complaint_no,
        reference_id: referenceId
      }
    );
  }
}
