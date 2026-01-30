import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { AuthService, User } from '../services/auth';
import { SessionService } from '../services/session';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './login.html',
  styleUrls: ['./login.css']
})
export class LoginComponent {

  email = '';
  password = '';
  successMessage = '';
  errorMessage = '';

  constructor(private router: Router, private authService: AuthService, private sessionService: SessionService) {

    // Show success message when redirected from signup
    const state = this.router.getCurrentNavigation()?.extras?.state as any;
    if (state?.['message']) {
      this.successMessage = state['message'];
    }
  }

onLogin() {
  this.errorMessage = '';
  this.successMessage = '';

  this.authService.login({ email: this.email, password: this.password }).subscribe({
    next: (user) => {
      if (!user) {
        this.errorMessage = 'Invalid email or password!';
        return;
      }

      this.sessionService.startTimer();

      switch (user.role) {
        case 'admin':
        case 'sub_admin':
          this.router.navigate(['/admin']);
          break;
        case 'staff':
          this.router.navigate(['/staff']);
          break;
        default:
          this.router.navigate(['/customer']);
      }
    },
    error: () => {
      this.errorMessage = 'Invalid email or password!';
    }
  });
}





}
