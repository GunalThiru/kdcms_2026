import { AuthGuard } from './guards/auth-guard';
import { Routes } from '@angular/router';
import { provideRouter } from '@angular/router';
import { LoginComponent } from './login/login';
import { SignupComponent } from './signup/signup';
import { Customer } from './customer/customer';
import { Staff } from './staff/staff';
import { ComplaintFormComponent } from './complaint-form/complaint-form';
import { ProfileComponent } from './profile/profile';
import { TasksComponent } from './staff/tasks/tasks'
import { Unauthorized } from './unauthorized/unauthorized';
import { Blank } from './blank/blank';
import { GuestComplaintComponent } from './guest-complaint/guest-complaint';
import { ComplaintReport } from  './complaint-report/complaint-report'
import { ComplaintList } from './complaint-list/complaint-list';
import { TrackComplaintComponent } from './track-complaint/track-complaint';


export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },

  { path: 'login', component: LoginComponent },
  { path: 'signup', component: SignupComponent },

  // 🔒 PROTECTED ROUTES
  {
    path: 'customer',
    component: Customer,
    canActivate: [AuthGuard]
  },
  {
  path: 'staff',
  component: Staff,
  canActivate: [AuthGuard],
  children: [
    {
      path: '',
      redirectTo: 'summary',
      pathMatch: 'full'
    },
    {
      path: 'summary',
      component: ComplaintReport
    },
    {
      path: 'complaints',
      component: ComplaintList
    },
    {
      path: 'tasks',
      component: TasksComponent
    },
    {
      path: 'new-complaint',
      component: ComplaintFormComponent
    }
  ]
},

  {
    path: 'complaint-form',
    component: ComplaintFormComponent,
    canActivate: [AuthGuard]
  },
  {
  path: 'guest-complaint',
  component:GuestComplaintComponent
  
     
}
,
{
    path: 'complaints-report',
    component: ComplaintReport
  },
  {
    path: 'complaints-list',
    component: ComplaintList
  },

  { path: 'profile/:id', 
    component: ProfileComponent,
     canActivate: [AuthGuard]  

  },
  {
    path: 'tasks',
    component: TasksComponent,
     canActivate: [AuthGuard] 
  },
  
  {
  path: 'unauthorized',
  component: Unauthorized
}
,
{

  path:'track-complaint',
  component:TrackComplaintComponent

},



  // 404
  { path: '**', component: Blank }
];

export const appRouter = provideRouter(routes);
