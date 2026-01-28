import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
@Component({
  selector: 'app-track-complaint',
  templateUrl: './track-complaint.html',
  styleUrls: ['./track-complaint.css'],
  imports: [CommonModule, FormsModule,RouterModule],
  standalone: true
})
export class TrackComplaintComponent {
  complaint_no!: string;
  referenceId = '';

  loading = false;
  error = '';
  result: any = null;

  constructor(private http: HttpClient) {}

  track() {
    this.error = '';
    this.result = null;

    if (!this.complaint_no || !this.referenceId) {
      this.error = 'Please enter Complaint No and Reference ID';
      return;
    }

    this.loading = true;
    

    this.http.post<any>('http://localhost:5000/complaints/track', {
      
      
      complaint_no: this.complaint_no.trim(),
      reference_id: this.referenceId.trim()
      
    }).subscribe({

      
      next: res => {
        this.result = res;
        this.loading = false;
        console.log("Tracking complaint with ID:", this.complaint_no, "and reference ID:", this.referenceId);
      },
      error: () => {
        this.error = 'No complaint found with provided details';
        console.log("Tracking complaint with ID:", this.complaint_no, "and reference ID:", this.referenceId);
        this.loading = false;
      }
    });
  }
}
