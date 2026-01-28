import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { BehaviorSubject, Observable, tap, map } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

export interface User {
  id: number;
  name: string;
  email: string;
  phone?: string;
  dob?: string;
  age?: number;
  role: 'admin' | 'sub_admin' | 'staff' | 'customer';
  is_online?: boolean;
  last_seen?: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private baseUrl = 'http://localhost:5000';
  private isBrowser: boolean;

  // Reactive user state
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  currentUser$ = this.currentUserSubject.asObservable();

  constructor(
    private http: HttpClient,
    private router: Router,
    @Inject(PLATFORM_ID) platformId: Object
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
    this.loadUserFromStorage();
  }

  // -----------------------------
  // LOAD USER FROM STORAGE
  // -----------------------------
  private loadUserFromStorage() {
    if (!this.isBrowser) return;
    const stored = localStorage.getItem('user') || sessionStorage.getItem('user');
    if (stored) {
      this.currentUserSubject.next(JSON.parse(stored));
    }
  }

  // -----------------------------
  // SIGNUP
  // -----------------------------
  signup(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/signup`, data);
  }

  // -----------------------------
  // LOGIN
  // -----------------------------
login(credentials: { email: string; password: string }): Observable<User | null> {
  return this.http.post<{
    message: string;
    access_token: string;
    user: User;
  }>(`${this.baseUrl}/auth/login`, credentials).pipe(

    tap(res => {
      if (!this.isBrowser) return;

      // ✅ Save token (SESSION STORAGE = multi-user demo)
      sessionStorage.setItem('access_token', res.access_token);
      sessionStorage.setItem('user', JSON.stringify(res.user));

      // cleanup
      localStorage.removeItem('user');

      // update reactive state
      this.currentUserSubject.next(res.user);
    }),

    // 🔁 Now return only user to components
    map(res => res.user ?? null)
  );
}


  // -----------------------------
  // LOGOUT
  // -----------------------------
 
logout(userId?: number) {

  // 🔥 Clear reactive state
  this.currentUserSubject.next(null);

  if (this.isBrowser) {
    localStorage.removeItem('user');
    sessionStorage.removeItem('user');
  }

  this.router.navigate(['/login']);

  if (userId) {
    return this.http.post(`${this.baseUrl}/auth/logout`, { user_id: userId });
  }

  return null;
}





  // -----------------------------
  // CURRENT USER
  // -----------------------------
  get currentUser(): User | null {
    return this.currentUserSubject.value;
  }

  isLoggedIn(): boolean {
    return !!this.currentUserSubject.value;
  }

  getUserRole(): string | null {
    return this.currentUserSubject.value?.role || null;
  }

  getUserId(): number | null {
    return this.currentUserSubject.value?.id || null;
  }
  getUserName(): string | null {
    return this.currentUserSubject.value?.name || null;
  } 

  // -----------------------------
  // HELPER TO FETCH ALL USERS
  // -----------------------------
  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(`${this.baseUrl}/users`);
  }

  // -----------------------------
  // SET USER MANUALLY
  // -----------------------------
  setCurrentUser(user: User | null, persist: boolean = true) {
    this.currentUserSubject.next(user);
    if (!this.isBrowser) return;
    if (user) {
      if (persist) localStorage.setItem('user', JSON.stringify(user));
      else sessionStorage.setItem('user', JSON.stringify(user));
    } else {
      localStorage.removeItem('user');
      sessionStorage.removeItem('user');
    }
  }
}
