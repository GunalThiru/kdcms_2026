import { TestBed } from '@angular/core/testing';

import { ComplaintEmailNotification } from './complaint-email-notification';

describe('ComplaintEmailNotification', () => {
  let service: ComplaintEmailNotification;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ComplaintEmailNotification);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
