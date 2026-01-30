import { Injectable, NgZone } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from './auth';

@Injectable({ providedIn: 'root' })
export class SessionService {
  private timeout: any;
  private readonly SESSION_TIME = 10 * 60 * 1000; // 10 minutes

  constructor(
    private router: Router,
    private authService: AuthService,
    private zone: NgZone
  ) {}

  startTimer() {
    this.clearTimer();
    this.timeout = setTimeout(() => {
      this.logout();
    }, this.SESSION_TIME);
  }

  resetTimer() {
    this.startTimer();
  }

  clearTimer() {
    if (this.timeout) {
      clearTimeout(this.timeout);
    }
  }

  logout() {
    // Clear timers
    this.clearTimer();

    // Use AuthService to properly logout and update reactive state
    this.zone.run(() => {
      this.authService.logout();
    });
  }
}
