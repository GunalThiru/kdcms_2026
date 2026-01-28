import { Injectable } from '@angular/core';
import { CanActivate, Router, ActivatedRouteSnapshot } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {

  constructor(private router: Router) {}

  canActivate(route: ActivatedRouteSnapshot): boolean {

    const userStr = sessionStorage.getItem('user');

    // 🔒 Not logged in
    if (!userStr) {
      this.router.navigate(['/login']);
      return false;
    }

    let role = '';
    try {
      role = JSON.parse(userStr).role || '';
    } catch {
      this.router.navigate(['/login']);
      return false;
    }

    const url = route.routeConfig?.path;

    // 🔐 Role-based checks
    if (url === 'staff' && role !== 'staff') {
      this.router.navigate(['/unauthorized']);
      return false;
    }

    if (url === 'customer' && role !== 'customer') {
      this.router.navigate(['/unauthorized']);
      return false;
    }

    if (url === 'complaint-form' && role !== 'customer') {
      this.router.navigate(['/unauthorized']);
      return false;
    }

    return true;
  }
}
