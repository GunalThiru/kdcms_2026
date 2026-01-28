import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ComplaintForm } from './complaint-form';

describe('ComplaintForm', () => {
  let component: ComplaintForm;
  let fixture: ComponentFixture<ComplaintForm>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ComplaintForm]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ComplaintForm);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
