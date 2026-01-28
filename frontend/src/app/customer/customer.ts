import { Component } from '@angular/core';
import { CommonModule } from '@angular/common'; 
import { ComplaintFormComponent } from '../complaint-form/complaint-form';

@Component({
  selector: 'app-customer',
  imports: [CommonModule, ComplaintFormComponent],
  templateUrl: './customer.html',
  styleUrl: './customer.css',
})
export class Customer {

 
}



