To create a flexible and reusable Angular PDF generation component, I’ll set up a configuration-based approach. This approach allows you to define templates with different layouts for forms like CPPA and LSCA, and the data will be mapped dynamically.

Step 1: Define Template Configurations

Create a JSON structure for each form template, specifying the layout, sections, and fields. This JSON configuration will allow you to add or modify templates without changing the main PDF generation code.

// form-templates.ts
export const formTemplates = {
  CPPA: {
    title: "California Participating Physician Application",
    sections: [
      {
        header: "I. INSTRUCTIONS",
        content: "This form should be typed or legibly printed...",
        fields: []
      },
      {
        header: "II. IDENTIFYING INFORMATION",
        fields: [
          { label: "Last Name:", valueKey: "lastName" },
          { label: "First Name:", valueKey: "firstName" },
          { label: "Middle:", valueKey: "middle" },
          { label: "Any other names:", valueKey: "otherNames" },
          { label: "Home Mailing Address:", valueKey: "homeAddress" },
          { label: "City:", valueKey: "city" },
          { label: "State:", valueKey: "state" },
          { label: "ZIP:", valueKey: "zip" },
          { label: "Home Telephone Number:", valueKey: "homePhone" },
          { label: "E-Mail Address:", valueKey: "email" },
          { label: "Citizenship:", valueKey: "citizenship" },
          { label: "Social Security #:", valueKey: "ssn" }
        ]
      },
      // Add more sections as needed
    ]
  },
  LSCA: {
    title: "Licensed Social Care Application",
    sections: [
      {
        header: "I. APPLICANT DETAILS",
        fields: [
          { label: "Applicant Name:", valueKey: "applicantName" },
          { label: "Date of Birth:", valueKey: "dob" },
          { label: "License Number:", valueKey: "licenseNumber" },
          { label: "Issuing State:", valueKey: "issuingState" }
        ]
      },
      // Define more sections specific to LSCA form
    ]
  }
};

Step 2: Update the Angular Component to Load the Template

In the component, we’ll load the selected form template and dynamically map data.

import { Component } from '@angular/core';
import * as pdfMake from 'pdfmake/build/pdfmake';
import * as pdfFonts from 'pdfmake/build/vfs_fonts';
import { formTemplates } from './form-templates';

pdfMake.vfs = pdfFonts.pdfMake.vfs;

@Component({
  selector: 'app-form-pdf',
  template: `
    <select [(ngModel)]="selectedTemplate" (change)="generatePDF()">
      <option *ngFor="let template of templateKeys" [value]="template">{{ template }}</option>
    </select>
    <button (click)="generatePDF()">Generate PDF</button>
  `,
  styleUrls: ['./form-pdf.component.css']
})
export class FormPdfComponent {
  selectedTemplate = 'CPPA';
  templateKeys = Object.keys(formTemplates);

  // Sample data; replace with actual form data
  formData = {
    lastName: "Doe",
    firstName: "John",
    middle: "M.",
    otherNames: "N/A",
    homeAddress: "123 Health St, Suite 200, San Francisco, CA",
    city: "San Francisco",
    state: "CA",
    zip: "94102",
    homePhone: "(555) 123-4567",
    email: "johndoe@example.com",
    citizenship: "USA",
    ssn: "XXX-XX-XXXX",
    applicantName: "Jane Doe",
    dob: "01/01/1980",
    licenseNumber: "123456",
    issuingState: "CA"
  };

  generatePDF() {
    const template = formTemplates[this.selectedTemplate];

    const content = [
      {
        text: template.title,
        style: 'header',
        alignment: 'center'
      }
    ];

    template.sections.forEach(section => {
      if (section.header) {
        content.push({
          text: section.header,
          style: 'sectionHeader'
        });
      }
      if (section.content) {
        content.push({
          text: section.content,
          style: 'content'
        });
      }
      section.fields.forEach(field => {
        content.push({
          columns: [
            { width: '30%', text: field.label, bold: true },
            { width: '70%', text: this.formData[field.valueKey] || '' }
          ]
        });
      });
    });

    const docDefinition = {
      content,
      styles: {
        header: {
          fontSize: 18,
          bold: true
        },
        sectionHeader: {
          fontSize: 12,
          bold: true,
          margin: [0, 10, 0, 5]
        },
        content: {
          fontSize: 10
        }
      }
    };

    pdfMake.createPdf(docDefinition).open();
  }
}

Explanation of the Code

	1.	Template Selection: The dropdown allows you to choose a template (e.g., CPPA, LSCA). This selection dynamically loads the corresponding structure.
	2.	Content Generation: The generatePDF function maps data based on valueKey in each field, making the layout reusable.
	3.	JSON-based Configuration: All form layouts are defined in form-templates.ts, making it easy to add or update templates without altering the main code.

Usage

	1.	Select a form template from the dropdown.
	2.	Click “Generate PDF” to see the dynamically generated form with the selected layout.

This structure lets you easily add new templates and data mappings by modifying the JSON configuration file. Let me know if you’d like further customization!