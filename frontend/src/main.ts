import { bootstrapApplication } from '@angular/platform-browser';
import { provideHttpClient, withInterceptors } from '@angular/common/http';

import { AppComponent } from './app/app';
import { appRouter } from './app/app.routes';
import { authInterceptor } from './app/interceptor/auth-interceptor';

bootstrapApplication(AppComponent, {
  providers: [
    appRouter,
    provideHttpClient(
      withInterceptors([authInterceptor])
    )
  ]
});
