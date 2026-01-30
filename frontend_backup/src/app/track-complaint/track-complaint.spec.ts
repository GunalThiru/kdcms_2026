import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TrackComplaint } from './track-complaint';

describe('TrackComplaint', () => {
  let component: TrackComplaint;
  let fixture: ComponentFixture<TrackComplaint>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TrackComplaint]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TrackComplaint);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
