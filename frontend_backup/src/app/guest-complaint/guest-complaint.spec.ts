import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GuestComplaint } from './guest-complaint';

describe('GuestComplaint', () => {
  let component: GuestComplaint;
  let fixture: ComponentFixture<GuestComplaint>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GuestComplaint]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GuestComplaint);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
