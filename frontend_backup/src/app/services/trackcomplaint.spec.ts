import { TestBed } from '@angular/core/testing';

import { Trackcomplaint } from './trackcomplaint';

describe('Trackcomplaint', () => {
  let service: Trackcomplaint;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Trackcomplaint);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
