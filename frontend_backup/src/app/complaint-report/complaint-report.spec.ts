import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ComplaintReport } from './complaint-report';

describe('ComplaintReport', () => {
  let component: ComplaintReport;
  let fixture: ComponentFixture<ComplaintReport>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ComplaintReport]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ComplaintReport);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
