import { Component, OnInit, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { FormsModule } from '@angular/forms';

import { AuthService } from './services/auth';
import { SessionService } from './services/session';
import { ComplaintService } from './services/complaint-service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule,RouterModule,FormsModule],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class AppComponent implements OnInit {

  userRole: string | null = null;
  userId: number | null = null;

  links: any[] = [];

  logoText = 'CMS';
  logoRoute = '/';

  // 🔔 Staff task count
  taskCount = 0;

  sideBarOpen = false;

  constructor(
    private router: Router,
    private authService: AuthService,
    private sessionService: SessionService,
    private complaintService: ComplaintService
  ) {}

  ngOnInit() {
    // Reactively update navbar on login/logout
    this.authService.currentUser$.subscribe(user => {
      this.userRole = user?.role || null;
      this.userId = user?.id || null;

      if (this.userRole === 'staff') {
        this.loadTaskCount();
      } else {
        this.taskCount = 0;
      }

      this.updateNavbar();

      if (user) {
        this.sessionService.startTimer();
      }
    });

    // Reload navbar on route change - close sidebar on mobile only
    this.router.events.pipe(filter(event => event instanceof NavigationEnd)).subscribe(() => {
      if (window.innerWidth < 1024) {
        this.sideBarOpen = false;
      }
    });
  }

  // 🔐 Session tracking
  @HostListener('document:mousemove')
  @HostListener('document:keydown')
  @HostListener('document:click')
  resetSession() {
    this.sessionService.resetTimer();
  }

  loadUserAndNavbar() {
    const userStr = sessionStorage.getItem('user');

    if (userStr) {
      const user = JSON.parse(userStr);
      this.userRole = user.role || null;
      this.userId = user.id || null;
    } else {
      this.userRole = null;
      this.userId = null;
    }

    if (this.userRole === 'staff') {
      this.loadTaskCount();
    }

    this.updateNavbar();
  }

  // 🔔 Fetch open task count
  loadTaskCount() {
    this.complaintService.getOpenTaskCount().subscribe({
      next: (response) => {
        this.taskCount = response.open_tasks;
        this.updateNavbar();
      },
      error: () => {
        this.taskCount = 0;
      }
    });
  }

  updateNavbar() {

    this.sideBarOpen = false; // auto-close on route / role change

    switch (this.userRole) {

      case 'admin':
      case 'sub_admin':
        this.logoText = 'Admin Panel';
        this.logoRoute = '/admin';
        this.links = [
          { label: 'Profile', route: ['/profile', this.userId] },
          { label: 'Users', route: '/admin/view-users' },
          { label: 'Logout', action: () => this.logout() }
        ];
        break;

      case 'staff':
        this.logoText = 'Staff Portal';
        this.logoRoute = '/staff';
        this.links = [
          {
            label: 'Tasks',
            route: '/tasks',
            badge: this.taskCount   // 🔔 badge count
          },
          { label: 'Profile', route: ['/profile', this.userId] },
          { label: 'Logout', action: () => this.logout() }
        ];
        break;

      case 'customer':
        this.logoText = 'Customer Portal';
        this.logoRoute = '/customer';
        this.links = [
          { label: 'My Complaints', route: '/customer/complaints' },
          { label: 'Profile', route: ['/profile', this.userId] },
          { label: 'History', route: '/history' },
          { label: 'Logout', action: () => this.logout() }
        ];
        break;

      default:
        this.logoText = 'CMS';
        this.logoRoute = '/';
        this.links = [
          { label: 'SignUp', route: '/signup' },
          { label: 'Login', route: '/login' }
        ];
    }
  }

logout() {
  const userId = this.userId ?? undefined;

  this.authService.logout(userId); // clears BehaviorSubject
}

// Close sidebar on link click (for mobile)
onSidebarLinkClick() {
  this.sideBarOpen = false;
}

// Handle action links and close sidebar
onSidebarActionClick(action: Function) {
  this.sideBarOpen = false;
  action();
}


  
}
