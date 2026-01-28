import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ProfileService {
  private apiUrl = 'http://localhost:5000/profile';

  constructor(private http: HttpClient) {}

  getProfile(userId: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/${userId}`);
  }

  updateProfile(userId: number, payload: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/${userId}`, payload);
  }
}
