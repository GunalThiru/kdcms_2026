import { TestBed } from '@angular/core/testing';

import { ReportingStaff } from './reporting-staff';

describe('ReportingStaff', () => {
  let service: ReportingStaff;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ReportingStaff);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
