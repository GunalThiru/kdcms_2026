import { Component, OnInit } from '@angular/core';

import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ProfileService } from '../services/profile';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './profile.html',
  styleUrls: ['./profile.css']
})
export class ProfileComponent implements OnInit {
  userId!: number;
  profile: any = {};
  isEditing = false;
  loading = true;
  error = '';
  successMessage = '';
  errorMessage = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private profileService: ProfileService
  ) {}

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (!idParam) {
      this.router.navigate(['/login']);
      return;
    }

    this.userId = Number(idParam);
    this.loadProfile();
  }

  loadProfile() {
    this.profileService.getProfile(this.userId).subscribe({
      next: (res) => {
        this.profile = res;
        this.loading = false;
      },
      error: () => {
        this.error = 'Unable to load profile';
        this.loading = false;
      }
    });
  }

  enableEdit() {
    this.isEditing = true;
  }

  cancelEdit() {
    this.isEditing = false;
    this.successMessage = '';
    this.errorMessage = '';
    this.loadProfile();
  }

  saveProfile() {
    const payload = {
      name: this.profile.name,
      phone: this.profile.phone,
      email: this.profile.email,
      gender: this.profile.gender,
      dob: this.profile.dob,
      age: this.profile.age
    };

    this.profileService.updateProfile(this.userId, payload).subscribe({
      next: () => {
        this.successMessage = `Profile updated successfully!`;
        this.errorMessage = '';
        this.isEditing = false;
        
        // Clear success message after 3 seconds
        setTimeout(() => {
          this.successMessage = '';
        }, 3000);
      },
      error: () => {
        this.errorMessage = 'Profile updation failed!';
        this.successMessage = '';
      }
    });
  }
}
