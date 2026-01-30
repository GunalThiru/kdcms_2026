import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ComplaintList } from './complaint-list';

describe('ComplaintList', () => {
  let component: ComplaintList;
  let fixture: ComponentFixture<ComplaintList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ComplaintList]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ComplaintList);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
