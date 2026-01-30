import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../services/auth';

@Component({
  selector: 'app-signup',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './signup.html',
  styleUrls: ['./signup.css']
})
export class SignupComponent {
  name = '';
  email = '';
  phone = '';
  gender = '';
  dob = '';
  age = 0;
  password = '';
  role: 'customer' = 'customer';

  successMessage = '';
  errorMessage = '';

  constructor(private authService: AuthService, private router: Router) {}

  // Calculate age from DOB
  calculateAge(): void {
    if (!this.dob) {
      this.age = 0;
      return;
    }

    const today = new Date();
    const birthDate = new Date(this.dob);
    let calculatedAge = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();

    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      calculatedAge--;
    }

    this.age = calculatedAge;
  }

  // Signup
  onSignup(): void {
    const userData = {
      name: this.name,
      email: this.email,
      phone: this.phone,
      gender: this.gender,
      dob: this.dob,
      age: this.age,
      password: this.password,
      role: this.role
    };

    this.authService.signup(userData).subscribe({
      next: () => {
        this.successMessage = 'Signup successful! Redirecting to login...';
        this.errorMessage = '';
        setTimeout(() => this.router.navigate(['/login']), 2000);
      },
      error: (err) => {
        this.errorMessage = err.error?.message || 'Signup failed! Try again.';
        this.successMessage = '';
      }
    });
  }
}
