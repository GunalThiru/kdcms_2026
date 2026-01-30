// guest-complaint.component.ts
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ComplaintFormComponent } from '../complaint-form/complaint-form';

@Component({
  selector: 'app-guest-complaint',
  standalone: true,
  imports: [CommonModule, FormsModule, ComplaintFormComponent],
  templateUrl: './guest-complaint.html',
  styleUrls: ['./guest-complaint.css']
})
export class GuestComplaintComponent {}
