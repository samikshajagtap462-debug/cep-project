/**
 * Shared Practical Batch & Class Formatting Utility
 */
function extractBatchLetter(batch) {
  if (!batch) return null;
  const s = String(batch).trim();
  if (/^[A-C]$/i.test(s)) return s.toUpperCase();
  const m = s.match(/(?:batch|division|div|sec)?[\s\-_:\(]*([A-C])(?:\)|$|\s)/i);
  if (m) return m[1].toUpperCase();
  const m2 = s.match(/([A-C])/i);
  if (m2) return m2[1].toUpperCase();
  const m3 = s.match(/([A-C])$/i);
  if (m3) return m3[1].toUpperCase();
  return s;
}

function formatClassWithBatch(classOrSession, batch, isLab) {
  if (classOrSession && typeof classOrSession === 'object') {
    const s = classOrSession;
    const base = (s.className || s.class_name || s.classDiv || '').replace(/-/g, ' ').replace(/\s*\([A-Za-z0-9\s]+\)$/, '').trim();
    const isPractical = s.isLab || s.is_lab || s.type === 'Lab Practical' || s.session_type === 'Practical';
    return formatClassWithBatch(base, s.batch, isPractical);
  }
  let base = (classOrSession || '').replace(/-/g, ' ').replace(/\s*\([A-Za-z0-9\s]+\)$/, '').trim();
  if (!base) return '';

  const bLetter = extractBatchLetter(batch);

  if (isLab) {
    if (bLetter) {
      return `${base} (${bLetter})`;
    } else {
      return `${base} (Batch Required)`;
    }
  }
  if (bLetter) {
    return `${base} (${bLetter})`;
  }
  return base;
}

if (typeof window !== 'undefined') {
  window.extractBatchLetter = extractBatchLetter;
  window.formatClassWithBatch = formatClassWithBatch;
}

/**
 * EduNova – Smart Faculty Timetable Management System
 * Shared Sample Timetable Data & Scheduling Utilities
 */

const EDUNOVA_FACULTY_ID = "FAC-ANA"; // Real AI&DS Faculty: Mrs. Ashvini N. Ahirrao // Logged-in Faculty: Prof. Sunita Sharma

const MASTER_TIMETABLE = [
  {
    "id": "SCH-001",
    "dbId": 1,
    "day": "Monday",
    "startTime": "09:00",
    "endTime": "10:00",
    "displayTime": "09:00 - 10:00",
    "subject": "Machine Learning",
    "facultyId": "FAC-101",
    "facultyDbId": 2,
    "facultyName": "Mrs. Ashvini N. Ahirrao",
    "classDiv": "TY AD1",
    "className": "TY-AD1",
    "room": "Room 101",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-003",
    "dbId": 3,
    "day": "Monday",
    "startTime": "11:15",
    "endTime": "12:15",
    "displayTime": "11:15 - 12:15",
    "subject": "Data Structures",
    "facultyId": "FAC-104",
    "facultyDbId": 5,
    "facultyName": "Dr. Kulkarni",
    "classDiv": "SY AD2",
    "className": "SY-AD2",
    "room": "Room 101",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-004",
    "dbId": 4,
    "day": "Monday",
    "startTime": "12:15",
    "endTime": "13:15",
    "displayTime": "12:15 - 13:15",
    "subject": "AI & Robotics",
    "facultyId": "FAC-103",
    "facultyDbId": 4,
    "facultyName": "Prof. Joshi",
    "classDiv": "BE AD1",
    "className": "BE-AD1",
    "room": "Lab 202",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-005",
    "dbId": 5,
    "day": "Tuesday",
    "startTime": "09:00",
    "endTime": "10:00",
    "displayTime": "09:00 - 10:00",
    "subject": "DBMS",
    "facultyId": null,
    "facultyDbId": null,
    "facultyName": "",
    "classDiv": "SY AD1",
    "className": "SY-AD1",
    "room": "Room 102",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-006",
    "dbId": 6,
    "day": "Tuesday",
    "startTime": "11:15",
    "endTime": "12:15",
    "displayTime": "11:15 - 12:15",
    "subject": "Computer Networks",
    "facultyId": "FAC-105",
    "facultyDbId": 6,
    "facultyName": "Prof. Pawar",
    "classDiv": "SY AD3",
    "className": "SY-AD3",
    "room": "Room 201",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-007",
    "dbId": 7,
    "day": "Tuesday",
    "startTime": "14:00",
    "endTime": "15:00",
    "displayTime": "14:00 - 15:00",
    "subject": "Advanced AI Topics",
    "facultyId": "FAC-101",
    "facultyDbId": 2,
    "facultyName": "Mrs. Ashvini N. Ahirrao",
    "classDiv": "BE AD2",
    "className": "BE-AD2",
    "room": "Room 102",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-008",
    "dbId": 8,
    "day": "Wednesday",
    "startTime": "09:00",
    "endTime": "10:00",
    "displayTime": "09:00 - 10:00",
    "subject": "Python Programming",
    "facultyId": "FAC-103",
    "facultyDbId": 4,
    "facultyName": "Prof. Joshi",
    "classDiv": "TY AD2",
    "className": "TY-AD2",
    "room": "Room 103",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-009",
    "dbId": 9,
    "day": "Monday",
    "startTime": "10:15",
    "endTime": "11:15",
    "displayTime": "10:15 - 11:15",
    "subject": "Problem Solving & Object-Oriented Programming",
    "facultyId": "FAC-ANA",
    "facultyDbId": 7,
    "facultyName": "Mrs. Ashvini N. Ahirrao",
    "classDiv": "SY AD1",
    "className": "SY-AD1",
    "room": "Room 102",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-010",
    "dbId": 10,
    "day": "Monday",
    "startTime": "11:15",
    "endTime": "12:15",
    "displayTime": "11:15 - 12:15",
    "subject": "Operating System & Administration",
    "facultyId": "FAC-SJN",
    "facultyDbId": 9,
    "facultyName": "Mrs. Sinu J. Nambiar",
    "classDiv": "SY AD1",
    "className": "SY-AD1",
    "room": "Room 102",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-011",
    "dbId": 11,
    "day": "Monday",
    "startTime": "13:00",
    "endTime": "14:00",
    "displayTime": "13:00 - 14:00",
    "subject": "Problem Solving & Object-Oriented Programming",
    "facultyId": "FAC-ANA",
    "facultyDbId": 7,
    "facultyName": "Mrs. Ashvini N. Ahirrao",
    "classDiv": "SY AD1",
    "className": "SY-AD1",
    "room": "Room 102",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-012",
    "dbId": 12,
    "day": "Monday",
    "startTime": "14:00",
    "endTime": "15:00",
    "displayTime": "14:00 - 15:00",
    "subject": "Discrete Mathematics",
    "facultyId": "FAC-ASS",
    "facultyDbId": 8,
    "facultyName": "Mrs. Abhilasha S. Shinde",
    "classDiv": "SY AD1",
    "className": "SY-AD1",
    "room": "Room 102",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-013",
    "dbId": 13,
    "day": "Monday",
    "startTime": "15:15",
    "endTime": "17:15",
    "displayTime": "15:15 - 17:15",
    "subject": "Operating Systems Laboratory",
    "facultyId": "FAC-SJN",
    "facultyDbId": 9,
    "facultyName": "Mrs. Sinu J. Nambiar",
    "classDiv": "SY AD1 (A)",
    "className": "SY-AD1",
    "room": "AI1",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-014",
    "dbId": 14,
    "day": "Monday",
    "startTime": "15:15",
    "endTime": "17:15",
    "displayTime": "15:15 - 17:15",
    "subject": "Community Engagement and Innovation Lab-I",
    "facultyId": "FAC-ASS",
    "facultyDbId": 8,
    "facultyName": "Mrs. Abhilasha S. Shinde",
    "classDiv": "SY AD1 (B)",
    "className": "SY-AD1",
    "room": "AI2",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-015",
    "dbId": 15,
    "day": "Monday",
    "startTime": "15:15",
    "endTime": "17:15",
    "displayTime": "15:15 - 17:15",
    "subject": "Scientific Research & Publication",
    "facultyId": "FAC-DRD",
    "facultyDbId": 19,
    "facultyName": "Dr. Dhanraj R. Dhotre",
    "classDiv": "SY AD1 (C)",
    "className": "SY-AD1",
    "room": "IIOT",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-016",
    "dbId": 16,
    "day": "Tuesday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Community Engagement and Innovation Lab-I",
    "facultyId": "FAC-ASS",
    "facultyDbId": 8,
    "facultyName": "Mrs. Abhilasha S. Shinde",
    "classDiv": "SY AD1 (A)",
    "className": "SY-AD1",
    "room": "AI2",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-017",
    "dbId": 17,
    "day": "Tuesday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Problem Solving & Object-Oriented Programming Lab",
    "facultyId": "FAC-ANA",
    "facultyDbId": 7,
    "facultyName": "Mrs. Ashvini N. Ahirrao",
    "classDiv": "SY AD1 (B)",
    "className": "SY-AD1",
    "room": "CN1",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-018",
    "dbId": 18,
    "day": "Tuesday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Professional Communication & Personality Development",
    "facultyId": "FAC-MK",
    "facultyDbId": 18,
    "facultyName": "Dr. Mrunal Kothari",
    "classDiv": "SY AD1 (C)",
    "className": "SY-AD1",
    "room": "Room 609A",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-019",
    "dbId": 19,
    "day": "Tuesday",
    "startTime": "10:15",
    "endTime": "12:15",
    "displayTime": "10:15 - 12:15",
    "subject": "Sustainable Engineering Practices",
    "facultyId": "FAC-VL",
    "facultyDbId": 10,
    "facultyName": "Dr. Vina Lomte",
    "classDiv": "SY AD1",
    "className": "SY-AD1",
    "room": "Room 103",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-020",
    "dbId": 20,
    "day": "Tuesday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Sustainable Engineering Practices Lab",
    "facultyId": "FAC-VL",
    "facultyDbId": 10,
    "facultyName": "Dr. Vina Lomte",
    "classDiv": "SY AD1 (A)",
    "className": "SY-AD1",
    "room": "AI1",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-021",
    "dbId": 21,
    "day": "Wednesday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Professional Communication & Personality Development",
    "facultyId": "FAC-MK",
    "facultyDbId": 18,
    "facultyName": "Dr. Mrunal Kothari",
    "classDiv": "SY AD1 (A)",
    "className": "SY-AD1",
    "room": "Room 609A",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-022",
    "dbId": 22,
    "day": "Wednesday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Community Engagement and Innovation Lab-I",
    "facultyId": "FAC-ASS",
    "facultyDbId": 8,
    "facultyName": "Mrs. Abhilasha S. Shinde",
    "classDiv": "SY AD1 (B)",
    "className": "SY-AD1",
    "room": "AI2",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-023",
    "dbId": 23,
    "day": "Wednesday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Operating Systems Laboratory",
    "facultyId": "FAC-SJN",
    "facultyDbId": 9,
    "facultyName": "Mrs. Sinu J. Nambiar",
    "classDiv": "SY AD1 (C)",
    "className": "SY-AD1",
    "room": "AI1",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-024",
    "dbId": 24,
    "day": "Wednesday",
    "startTime": "10:15",
    "endTime": "11:15",
    "displayTime": "10:15 - 11:15",
    "subject": "Discrete Mathematics",
    "facultyId": "FAC-ASS",
    "facultyDbId": 8,
    "facultyName": "Mrs. Abhilasha S. Shinde",
    "classDiv": "SY AD1",
    "className": "SY-AD1",
    "room": "Room 103",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-025",
    "dbId": 25,
    "day": "Wednesday",
    "startTime": "11:15",
    "endTime": "12:15",
    "displayTime": "11:15 - 12:15",
    "subject": "Operating System & Administration",
    "facultyId": "FAC-SJN",
    "facultyDbId": 9,
    "facultyName": "Mrs. Sinu J. Nambiar",
    "classDiv": "SY AD1",
    "className": "SY-AD1",
    "room": "Room 103",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-026",
    "dbId": 26,
    "day": "Wednesday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Scientific Research & Publication",
    "facultyId": "FAC-DRD",
    "facultyDbId": 19,
    "facultyName": "Dr. Dhanraj R. Dhotre",
    "classDiv": "SY AD1 (A)",
    "className": "SY-AD1",
    "room": "IIOT",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-027",
    "dbId": 27,
    "day": "Wednesday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Professional Communication & Personality Development",
    "facultyId": "FAC-MK",
    "facultyDbId": 18,
    "facultyName": "Dr. Mrunal Kothari",
    "classDiv": "SY AD1 (B)",
    "className": "SY-AD1",
    "room": "Room MB614",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-028",
    "dbId": 28,
    "day": "Wednesday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Community Engagement and Innovation Lab-I",
    "facultyId": "FAC-GR",
    "facultyDbId": 16,
    "facultyName": "Mrs. Gayatri Rukare",
    "classDiv": "SY AD1 (C)",
    "className": "SY-AD1",
    "room": "ARVR",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-029",
    "dbId": 29,
    "day": "Thursday",
    "startTime": "08:00",
    "endTime": "09:00",
    "displayTime": "08:00 - 09:00",
    "subject": "Operating System & Administration",
    "facultyId": "FAC-SJN",
    "facultyDbId": 9,
    "facultyName": "Mrs. Sinu J. Nambiar",
    "classDiv": "SY AD1",
    "className": "SY-AD1",
    "room": "Room 102",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-030",
    "dbId": 30,
    "day": "Thursday",
    "startTime": "09:00",
    "endTime": "10:00",
    "displayTime": "09:00 - 10:00",
    "subject": "Discrete Mathematics",
    "facultyId": "FAC-ASS",
    "facultyDbId": 8,
    "facultyName": "Mrs. Abhilasha S. Shinde",
    "classDiv": "SY AD1",
    "className": "SY-AD1",
    "room": "Room 102",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-031",
    "dbId": 31,
    "day": "Thursday",
    "startTime": "10:15",
    "endTime": "12:15",
    "displayTime": "10:15 - 12:15",
    "subject": "Community Engagement and Innovation Lab-I",
    "facultyId": "FAC-ASS",
    "facultyDbId": 8,
    "facultyName": "Mrs. Abhilasha S. Shinde",
    "classDiv": "SY AD1 (A)",
    "className": "SY-AD1",
    "room": "ARVR",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-032",
    "dbId": 32,
    "day": "Thursday",
    "startTime": "10:15",
    "endTime": "12:15",
    "displayTime": "10:15 - 12:15",
    "subject": "Scientific Research & Publication",
    "facultyId": "FAC-DRD",
    "facultyDbId": 19,
    "facultyName": "Dr. Dhanraj R. Dhotre",
    "classDiv": "SY AD1 (B)",
    "className": "SY-AD1",
    "room": "IIOT",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-033",
    "dbId": 33,
    "day": "Thursday",
    "startTime": "10:15",
    "endTime": "12:15",
    "displayTime": "10:15 - 12:15",
    "subject": "Problem Solving & Object-Oriented Programming Lab",
    "facultyId": "FAC-ANA",
    "facultyDbId": 7,
    "facultyName": "Mrs. Ashvini N. Ahirrao",
    "classDiv": "SY AD1 (C)",
    "className": "SY-AD1",
    "room": "CN1",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-034",
    "dbId": 34,
    "day": "Thursday",
    "startTime": "13:00",
    "endTime": "14:00",
    "displayTime": "13:00 - 14:00",
    "subject": "Problem Solving & Object-Oriented Programming",
    "facultyId": "FAC-ANA",
    "facultyDbId": 7,
    "facultyName": "Mrs. Ashvini N. Ahirrao",
    "classDiv": "SY AD1",
    "className": "SY-AD1",
    "room": "Room 102",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-035",
    "dbId": 35,
    "day": "Friday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Problem Solving & Object-Oriented Programming Lab",
    "facultyId": "FAC-ANA",
    "facultyDbId": 7,
    "facultyName": "Mrs. Ashvini N. Ahirrao",
    "classDiv": "SY AD1 (A)",
    "className": "SY-AD1",
    "room": "CN1",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-036",
    "dbId": 36,
    "day": "Friday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Operating Systems Laboratory",
    "facultyId": "FAC-SJN",
    "facultyDbId": 9,
    "facultyName": "Mrs. Sinu J. Nambiar",
    "classDiv": "SY AD1 (B)",
    "className": "SY-AD1",
    "room": "AI1",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-037",
    "dbId": 37,
    "day": "Friday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Community Engagement and Innovation Lab-I",
    "facultyId": "FAC-GR",
    "facultyDbId": 16,
    "facultyName": "Mrs. Gayatri Rukare",
    "classDiv": "SY AD1 (C)",
    "className": "SY-AD1",
    "room": "AI2",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-038",
    "dbId": 38,
    "day": "Friday",
    "startTime": "10:15",
    "endTime": "12:15",
    "displayTime": "10:15 - 12:15",
    "subject": "Sustainable Engineering Practices Lab",
    "facultyId": "FAC-VL",
    "facultyDbId": 10,
    "facultyName": "Dr. Vina Lomte",
    "classDiv": "SY AD1 (B)",
    "className": "SY-AD1",
    "room": "AI1",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-039",
    "dbId": 39,
    "day": "Friday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Sustainable Engineering Practices Lab",
    "facultyId": "FAC-VL",
    "facultyDbId": 10,
    "facultyName": "Dr. Vina Lomte",
    "classDiv": "SY AD1 (C)",
    "className": "SY-AD1",
    "room": "AI1",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-040",
    "dbId": 40,
    "day": "Friday",
    "startTime": "16:15",
    "endTime": "17:15",
    "displayTime": "16:15 - 17:15",
    "subject": "Universal Human Values",
    "facultyId": "FAC-ANA",
    "facultyDbId": 7,
    "facultyName": "Mrs. Ashvini N. Ahirrao",
    "classDiv": "SY AD1",
    "className": "SY-AD1",
    "room": "Room 102",
    "batch": null,
    "type": "Tutorial",
    "isLab": false
  },
  {
    "id": "SCH-041",
    "dbId": 41,
    "day": "Monday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Professional Communication & Personality Development",
    "facultyId": "FAC-MK",
    "facultyDbId": 18,
    "facultyName": "Dr. Mrunal Kothari",
    "classDiv": "SY AD2 (A)",
    "className": "SY-AD2",
    "room": "Room 609A",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-042",
    "dbId": 42,
    "day": "Monday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Operating Systems Laboratory",
    "facultyId": "FAC-KPS",
    "facultyDbId": 13,
    "facultyName": "Mrs. Kalpna P. Saharan",
    "classDiv": "SY AD2 (B)",
    "className": "SY-AD2",
    "room": "ARVR",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-043",
    "dbId": 43,
    "day": "Monday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Problem Solving & Object-Oriented Programming Lab",
    "facultyId": "FAC-MKM",
    "facultyDbId": 11,
    "facultyName": "Dr. M. K. Mokashi",
    "classDiv": "SY AD2 (C)",
    "className": "SY-AD2",
    "room": "Room 609B",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-044",
    "dbId": 44,
    "day": "Monday",
    "startTime": "10:15",
    "endTime": "11:15",
    "displayTime": "10:15 - 11:15",
    "subject": "Problem Solving & Object-Oriented Programming",
    "facultyId": "FAC-MKM",
    "facultyDbId": 11,
    "facultyName": "Dr. M. K. Mokashi",
    "classDiv": "SY AD2",
    "className": "SY-AD2",
    "room": "Room 104",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-045",
    "dbId": 45,
    "day": "Monday",
    "startTime": "11:15",
    "endTime": "12:15",
    "displayTime": "11:15 - 12:15",
    "subject": "Discrete Mathematics",
    "facultyId": "FAC-SDJ",
    "facultyDbId": 12,
    "facultyName": "Mrs. Swati D. Jakkan",
    "classDiv": "SY AD2",
    "className": "SY-AD2",
    "room": "Room 104",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-046",
    "dbId": 46,
    "day": "Monday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Operating Systems Laboratory",
    "facultyId": "FAC-KPS",
    "facultyDbId": 13,
    "facultyName": "Mrs. Kalpna P. Saharan",
    "classDiv": "SY AD2 (A)",
    "className": "SY-AD2",
    "room": "AI1",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-047",
    "dbId": 47,
    "day": "Monday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Community Engagement and Innovation Lab-I",
    "facultyId": "FAC-SDJ",
    "facultyDbId": 12,
    "facultyName": "Mrs. Swati D. Jakkan",
    "classDiv": "SY AD2 (B)",
    "className": "SY-AD2",
    "room": "Room 609A",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-048",
    "dbId": 48,
    "day": "Monday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Scientific Research & Publication",
    "facultyId": "FAC-VL",
    "facultyDbId": 10,
    "facultyName": "Dr. Vina Lomte",
    "classDiv": "SY AD2 (C)",
    "className": "SY-AD2",
    "room": "Room 609B",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-049",
    "dbId": 49,
    "day": "Tuesday",
    "startTime": "08:00",
    "endTime": "09:00",
    "displayTime": "08:00 - 09:00",
    "subject": "Discrete Mathematics",
    "facultyId": "FAC-SDJ",
    "facultyDbId": 12,
    "facultyName": "Mrs. Swati D. Jakkan",
    "classDiv": "SY AD2",
    "className": "SY-AD2",
    "room": "Room 102",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-050",
    "dbId": 50,
    "day": "Tuesday",
    "startTime": "09:00",
    "endTime": "10:00",
    "displayTime": "09:00 - 10:00",
    "subject": "Operating System & Administration",
    "facultyId": "FAC-KPS",
    "facultyDbId": 13,
    "facultyName": "Mrs. Kalpna P. Saharan",
    "classDiv": "SY AD2",
    "className": "SY-AD2",
    "room": "Room 102",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-051",
    "dbId": 51,
    "day": "Tuesday",
    "startTime": "10:15",
    "endTime": "12:15",
    "displayTime": "10:15 - 12:15",
    "subject": "Sustainable Engineering Practices",
    "facultyId": "FAC-VL",
    "facultyDbId": 10,
    "facultyName": "Dr. Vina Lomte",
    "classDiv": "SY AD2",
    "className": "SY-AD2",
    "room": "Room 103",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-052",
    "dbId": 52,
    "day": "Tuesday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Sustainable Engineering Practices Lab",
    "facultyId": "FAC-VL",
    "facultyDbId": 10,
    "facultyName": "Dr. Vina Lomte",
    "classDiv": "SY AD2 (A)",
    "className": "SY-AD2",
    "room": "AI1",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-053",
    "dbId": 53,
    "day": "Wednesday",
    "startTime": "10:15",
    "endTime": "12:15",
    "displayTime": "10:15 - 12:15",
    "subject": "Scientific Research & Publication",
    "facultyId": "FAC-VL",
    "facultyDbId": 10,
    "facultyName": "Dr. Vina Lomte",
    "classDiv": "SY AD2 (A)",
    "className": "SY-AD2",
    "room": "Room 609A",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-054",
    "dbId": 54,
    "day": "Wednesday",
    "startTime": "10:15",
    "endTime": "12:15",
    "displayTime": "10:15 - 12:15",
    "subject": "Problem Solving & Object-Oriented Programming Lab",
    "facultyId": "FAC-MKM",
    "facultyDbId": 11,
    "facultyName": "Dr. M. K. Mokashi",
    "classDiv": "SY AD2 (B)",
    "className": "SY-AD2",
    "room": "Room 609B",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-055",
    "dbId": 55,
    "day": "Wednesday",
    "startTime": "10:15",
    "endTime": "12:15",
    "displayTime": "10:15 - 12:15",
    "subject": "Operating Systems Laboratory",
    "facultyId": "FAC-KPS",
    "facultyDbId": 13,
    "facultyName": "Mrs. Kalpna P. Saharan",
    "classDiv": "SY AD2 (C)",
    "className": "SY-AD2",
    "room": "AI2",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-056",
    "dbId": 56,
    "day": "Wednesday",
    "startTime": "13:00",
    "endTime": "14:00",
    "displayTime": "13:00 - 14:00",
    "subject": "Discrete Mathematics",
    "facultyId": "FAC-SDJ",
    "facultyDbId": 12,
    "facultyName": "Mrs. Swati D. Jakkan",
    "classDiv": "SY AD2",
    "className": "SY-AD2",
    "room": "Room 102",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-057",
    "dbId": 57,
    "day": "Wednesday",
    "startTime": "14:00",
    "endTime": "15:00",
    "displayTime": "14:00 - 15:00",
    "subject": "Problem Solving & Object-Oriented Programming",
    "facultyId": "FAC-MKM",
    "facultyDbId": 11,
    "facultyName": "Dr. M. K. Mokashi",
    "classDiv": "SY AD2",
    "className": "SY-AD2",
    "room": "Room 102",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-058",
    "dbId": 58,
    "day": "Wednesday",
    "startTime": "15:15",
    "endTime": "17:15",
    "displayTime": "15:15 - 17:15",
    "subject": "Community Engagement and Innovation Lab-I",
    "facultyId": "FAC-KPS",
    "facultyDbId": 13,
    "facultyName": "Mrs. Kalpna P. Saharan",
    "classDiv": "SY AD2 (A)",
    "className": "SY-AD2",
    "room": "AI1",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-059",
    "dbId": 59,
    "day": "Wednesday",
    "startTime": "15:15",
    "endTime": "17:15",
    "displayTime": "15:15 - 17:15",
    "subject": "Scientific Research & Publication",
    "facultyId": "FAC-VL",
    "facultyDbId": 10,
    "facultyName": "Dr. Vina Lomte",
    "classDiv": "SY AD2 (B)",
    "className": "SY-AD2",
    "room": "Room 609A",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-060",
    "dbId": 60,
    "day": "Wednesday",
    "startTime": "15:15",
    "endTime": "17:15",
    "displayTime": "15:15 - 17:15",
    "subject": "Community Engagement and Innovation Lab-I",
    "facultyId": "FAC-SDJ",
    "facultyDbId": 12,
    "facultyName": "Mrs. Swati D. Jakkan",
    "classDiv": "SY AD2 (C)",
    "className": "SY-AD2",
    "room": "IIOT",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-061",
    "dbId": 61,
    "day": "Thursday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Problem Solving & Object-Oriented Programming Lab",
    "facultyId": "FAC-MKM",
    "facultyDbId": 11,
    "facultyName": "Dr. M. K. Mokashi",
    "classDiv": "SY AD2 (A)",
    "className": "SY-AD2",
    "room": "Room 609B",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-062",
    "dbId": 62,
    "day": "Thursday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Community Engagement and Innovation Lab-I",
    "facultyId": "FAC-SDJ",
    "facultyDbId": 12,
    "facultyName": "Mrs. Swati D. Jakkan",
    "classDiv": "SY AD2 (B)",
    "className": "SY-AD2",
    "room": "IIOT",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-063",
    "dbId": 63,
    "day": "Thursday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Professional Communication & Personality Development",
    "facultyId": "FAC-MK",
    "facultyDbId": 18,
    "facultyName": "Dr. Mrunal Kothari",
    "classDiv": "SY AD2 (C)",
    "className": "SY-AD2",
    "room": "Room 104",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-064",
    "dbId": 64,
    "day": "Thursday",
    "startTime": "10:15",
    "endTime": "11:15",
    "displayTime": "10:15 - 11:15",
    "subject": "Problem Solving & Object-Oriented Programming",
    "facultyId": "FAC-MKM",
    "facultyDbId": 11,
    "facultyName": "Dr. M. K. Mokashi",
    "classDiv": "SY AD2",
    "className": "SY-AD2",
    "room": "Room 102",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-065",
    "dbId": 65,
    "day": "Thursday",
    "startTime": "11:15",
    "endTime": "12:15",
    "displayTime": "11:15 - 12:15",
    "subject": "Operating System & Administration",
    "facultyId": "FAC-KPS",
    "facultyDbId": 13,
    "facultyName": "Mrs. Kalpna P. Saharan",
    "classDiv": "SY AD2",
    "className": "SY-AD2",
    "room": "Room 102",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-066",
    "dbId": 66,
    "day": "Thursday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Community Engagement and Innovation Lab-I",
    "facultyId": "FAC-KPS",
    "facultyDbId": 13,
    "facultyName": "Mrs. Kalpna P. Saharan",
    "classDiv": "SY AD2 (A)",
    "className": "SY-AD2",
    "room": "AI1",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-067",
    "dbId": 67,
    "day": "Thursday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Professional Communication & Personality Development",
    "facultyId": "FAC-MK",
    "facultyDbId": 18,
    "facultyName": "Dr. Mrunal Kothari",
    "classDiv": "SY AD2 (B)",
    "className": "SY-AD2",
    "room": "Room MB614",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-068",
    "dbId": 68,
    "day": "Thursday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Community Engagement and Innovation Lab-I",
    "facultyId": "FAC-SDJ",
    "facultyDbId": 12,
    "facultyName": "Mrs. Swati D. Jakkan",
    "classDiv": "SY AD2 (C)",
    "className": "SY-AD2",
    "room": "IIOT",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-069",
    "dbId": 69,
    "day": "Friday",
    "startTime": "09:00",
    "endTime": "10:00",
    "displayTime": "09:00 - 10:00",
    "subject": "Operating System & Administration",
    "facultyId": "FAC-KPS",
    "facultyDbId": 13,
    "facultyName": "Mrs. Kalpna P. Saharan",
    "classDiv": "SY AD2",
    "className": "SY-AD2",
    "room": "Room 102",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-070",
    "dbId": 70,
    "day": "Friday",
    "startTime": "10:15",
    "endTime": "12:15",
    "displayTime": "10:15 - 12:15",
    "subject": "Sustainable Engineering Practices Lab",
    "facultyId": "FAC-VL",
    "facultyDbId": 10,
    "facultyName": "Dr. Vina Lomte",
    "classDiv": "SY AD2 (B)",
    "className": "SY-AD2",
    "room": "AI1",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-071",
    "dbId": 71,
    "day": "Friday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Sustainable Engineering Practices Lab",
    "facultyId": "FAC-VL",
    "facultyDbId": 10,
    "facultyName": "Dr. Vina Lomte",
    "classDiv": "SY AD2 (C)",
    "className": "SY-AD2",
    "room": "AI1",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-072",
    "dbId": 72,
    "day": "Friday",
    "startTime": "16:15",
    "endTime": "17:15",
    "displayTime": "16:15 - 17:15",
    "subject": "Universal Human Values",
    "facultyId": "FAC-SDJ",
    "facultyDbId": 12,
    "facultyName": "Mrs. Swati D. Jakkan",
    "classDiv": "SY AD2",
    "className": "SY-AD2",
    "room": "Room 104",
    "batch": null,
    "type": "Tutorial",
    "isLab": false
  },
  {
    "id": "SCH-073",
    "dbId": 73,
    "day": "Monday",
    "startTime": "09:00",
    "endTime": "10:00",
    "displayTime": "09:00 - 10:00",
    "subject": "Operating System & Administration",
    "facultyId": "FAC-DAG",
    "facultyDbId": 15,
    "facultyName": "Mrs. Dhanashree A. Gore",
    "classDiv": "SY AD3",
    "className": "SY-AD3",
    "room": "Room 103",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-074",
    "dbId": 74,
    "day": "Monday",
    "startTime": "10:15",
    "endTime": "11:15",
    "displayTime": "10:15 - 11:15",
    "subject": "Problem Solving & Object-Oriented Programming",
    "facultyId": "FAC-SAK",
    "facultyDbId": 14,
    "facultyName": "Mrs. Shruti A. Kulkarni",
    "classDiv": "SY AD3",
    "className": "SY-AD3",
    "room": "Room 103",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-075",
    "dbId": 75,
    "day": "Monday",
    "startTime": "11:15",
    "endTime": "12:15",
    "displayTime": "11:15 - 12:15",
    "subject": "Discrete Mathematics",
    "facultyId": "FAC-ASS",
    "facultyDbId": 8,
    "facultyName": "Mrs. Abhilasha S. Shinde",
    "classDiv": "SY AD3",
    "className": "SY-AD3",
    "room": "Room 103",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-076",
    "dbId": 76,
    "day": "Monday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Professional Communication & Personality Development",
    "facultyId": "FAC-MK",
    "facultyDbId": 18,
    "facultyName": "Dr. Mrunal Kothari",
    "classDiv": "SY AD3 (A)",
    "className": "SY-AD3",
    "room": "IIOT",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-077",
    "dbId": 77,
    "day": "Monday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Scientific Research & Publication",
    "facultyId": "FAC-MKM",
    "facultyDbId": 11,
    "facultyName": "Dr. M. K. Mokashi",
    "classDiv": "SY AD3 (B)",
    "className": "SY-AD3",
    "room": "ARVR",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-078",
    "dbId": 78,
    "day": "Monday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Community Engagement and Innovation Lab-I",
    "facultyId": "FAC-SDK",
    "facultyDbId": 17,
    "facultyName": "Mrs. Supriya D. Kapase",
    "classDiv": "SY AD3 (C)",
    "className": "SY-AD3",
    "room": "CN1",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-079",
    "dbId": 79,
    "day": "Tuesday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Community Engagement and Innovation Lab-I",
    "facultyId": "FAC-GR",
    "facultyDbId": 16,
    "facultyName": "Mrs. Gayatri Rukare",
    "classDiv": "SY AD3 (A)",
    "className": "SY-AD3",
    "room": "ARVR",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-080",
    "dbId": 80,
    "day": "Tuesday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Problem Solving & Object-Oriented Programming Lab",
    "facultyId": "FAC-SAK",
    "facultyDbId": 14,
    "facultyName": "Mrs. Shruti A. Kulkarni",
    "classDiv": "SY AD3 (B)",
    "className": "SY-AD3",
    "room": "AI1",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-081",
    "dbId": 81,
    "day": "Tuesday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Operating Systems Laboratory",
    "facultyId": "FAC-DAG",
    "facultyDbId": 15,
    "facultyName": "Mrs. Dhanashree A. Gore",
    "classDiv": "SY AD3 (C)",
    "className": "SY-AD3",
    "room": "IIOT",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-082",
    "dbId": 82,
    "day": "Tuesday",
    "startTime": "10:15",
    "endTime": "12:15",
    "displayTime": "10:15 - 12:15",
    "subject": "Sustainable Engineering Practices",
    "facultyId": "FAC-VL",
    "facultyDbId": 10,
    "facultyName": "Dr. Vina Lomte",
    "classDiv": "SY AD3",
    "className": "SY-AD3",
    "room": "Room 103",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-083",
    "dbId": 83,
    "day": "Tuesday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Sustainable Engineering Practices Lab",
    "facultyId": "FAC-VL",
    "facultyDbId": 10,
    "facultyName": "Dr. Vina Lomte",
    "classDiv": "SY AD3 (A)",
    "className": "SY-AD3",
    "room": "AI1",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-084",
    "dbId": 84,
    "day": "Wednesday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Scientific Research & Publication",
    "facultyId": "FAC-MKM",
    "facultyDbId": 11,
    "facultyName": "Dr. M. K. Mokashi",
    "classDiv": "SY AD3 (A)",
    "className": "SY-AD3",
    "room": "CN1",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-085",
    "dbId": 85,
    "day": "Wednesday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Operating Systems Laboratory",
    "facultyId": "FAC-DAG",
    "facultyDbId": 15,
    "facultyName": "Mrs. Dhanashree A. Gore",
    "classDiv": "SY AD3 (B)",
    "className": "SY-AD3",
    "room": "IIOT",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-086",
    "dbId": 86,
    "day": "Wednesday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Problem Solving & Object-Oriented Programming Lab",
    "facultyId": "FAC-SAK",
    "facultyDbId": 14,
    "facultyName": "Mrs. Shruti A. Kulkarni",
    "classDiv": "SY AD3 (C)",
    "className": "SY-AD3",
    "room": "ARVR",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-087",
    "dbId": 87,
    "day": "Wednesday",
    "startTime": "10:15",
    "endTime": "12:15",
    "displayTime": "10:15 - 12:15",
    "subject": "Community Engagement and Innovation Lab-I",
    "facultyId": "FAC-GR",
    "facultyDbId": 16,
    "facultyName": "Mrs. Gayatri Rukare",
    "classDiv": "SY AD3 (A)",
    "className": "SY-AD3",
    "room": "AI1",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-088",
    "dbId": 88,
    "day": "Wednesday",
    "startTime": "10:15",
    "endTime": "12:15",
    "displayTime": "10:15 - 12:15",
    "subject": "Community Engagement and Innovation Lab-I",
    "facultyId": "FAC-SDK",
    "facultyDbId": 17,
    "facultyName": "Mrs. Supriya D. Kapase",
    "classDiv": "SY AD3 (B)",
    "className": "SY-AD3",
    "room": "CN1",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-089",
    "dbId": 89,
    "day": "Wednesday",
    "startTime": "10:15",
    "endTime": "12:15",
    "displayTime": "10:15 - 12:15",
    "subject": "Professional Communication & Personality Development",
    "facultyId": "FAC-MK",
    "facultyDbId": 18,
    "facultyName": "Dr. Mrunal Kothari",
    "classDiv": "SY AD3 (C)",
    "className": "SY-AD3",
    "room": "ARVR",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-090",
    "dbId": 90,
    "day": "Wednesday",
    "startTime": "13:00",
    "endTime": "14:00",
    "displayTime": "13:00 - 14:00",
    "subject": "Operating System & Administration",
    "facultyId": "FAC-DAG",
    "facultyDbId": 15,
    "facultyName": "Mrs. Dhanashree A. Gore",
    "classDiv": "SY AD3",
    "className": "SY-AD3",
    "room": "Room 103",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-091",
    "dbId": 91,
    "day": "Wednesday",
    "startTime": "14:00",
    "endTime": "15:00",
    "displayTime": "14:00 - 15:00",
    "subject": "Discrete Mathematics",
    "facultyId": "FAC-ASS",
    "facultyDbId": 8,
    "facultyName": "Mrs. Abhilasha S. Shinde",
    "classDiv": "SY AD3",
    "className": "SY-AD3",
    "room": "Room 103",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-092",
    "dbId": 92,
    "day": "Thursday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Operating Systems Laboratory",
    "facultyId": "FAC-DAG",
    "facultyDbId": 15,
    "facultyName": "Mrs. Dhanashree A. Gore",
    "classDiv": "SY AD3 (A)",
    "className": "SY-AD3",
    "room": "AI1",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-093",
    "dbId": 93,
    "day": "Thursday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Community Engagement and Innovation Lab-I",
    "facultyId": "FAC-SDK",
    "facultyDbId": 17,
    "facultyName": "Mrs. Supriya D. Kapase",
    "classDiv": "SY AD3 (B)",
    "className": "SY-AD3",
    "room": "ARVR",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-094",
    "dbId": 94,
    "day": "Thursday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Scientific Research & Publication",
    "facultyId": "FAC-ANA",
    "facultyDbId": 7,
    "facultyName": "Mrs. Ashvini N. Ahirrao",
    "classDiv": "SY AD3 (C)",
    "className": "SY-AD3",
    "room": "CN1",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-095",
    "dbId": 95,
    "day": "Thursday",
    "startTime": "10:15",
    "endTime": "11:15",
    "displayTime": "10:15 - 11:15",
    "subject": "Operating System & Administration",
    "facultyId": "FAC-DAG",
    "facultyDbId": 15,
    "facultyName": "Mrs. Dhanashree A. Gore",
    "classDiv": "SY AD3",
    "className": "SY-AD3",
    "room": "Room 103",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-096",
    "dbId": 96,
    "day": "Thursday",
    "startTime": "11:15",
    "endTime": "12:15",
    "displayTime": "11:15 - 12:15",
    "subject": "Problem Solving & Object-Oriented Programming",
    "facultyId": "FAC-SAK",
    "facultyDbId": 14,
    "facultyName": "Mrs. Shruti A. Kulkarni",
    "classDiv": "SY AD3",
    "className": "SY-AD3",
    "room": "Room 103",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-097",
    "dbId": 97,
    "day": "Thursday",
    "startTime": "13:00",
    "endTime": "14:00",
    "displayTime": "13:00 - 14:00",
    "subject": "Discrete Mathematics",
    "facultyId": "FAC-ASS",
    "facultyDbId": 8,
    "facultyName": "Mrs. Abhilasha S. Shinde",
    "classDiv": "SY AD3",
    "className": "SY-AD3",
    "room": "Room 103",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-098",
    "dbId": 98,
    "day": "Thursday",
    "startTime": "14:00",
    "endTime": "15:00",
    "displayTime": "14:00 - 15:00",
    "subject": "Problem Solving & Object-Oriented Programming",
    "facultyId": "FAC-SAK",
    "facultyDbId": 14,
    "facultyName": "Mrs. Shruti A. Kulkarni",
    "classDiv": "SY AD3",
    "className": "SY-AD3",
    "room": "Room 103",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-099",
    "dbId": 99,
    "day": "Friday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Problem Solving & Object-Oriented Programming Lab",
    "facultyId": "FAC-SAK",
    "facultyDbId": 14,
    "facultyName": "Mrs. Shruti A. Kulkarni",
    "classDiv": "SY AD3 (A)",
    "className": "SY-AD3",
    "room": "ARVR",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-100",
    "dbId": 100,
    "day": "Friday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Professional Communication & Personality Development",
    "facultyId": "FAC-MK",
    "facultyDbId": 18,
    "facultyName": "Dr. Mrunal Kothari",
    "classDiv": "SY AD3 (B)",
    "className": "SY-AD3",
    "room": "Room 609A",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-101",
    "dbId": 101,
    "day": "Friday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Community Engagement and Innovation Lab-I",
    "facultyId": "FAC-SDK",
    "facultyDbId": 17,
    "facultyName": "Mrs. Supriya D. Kapase",
    "classDiv": "SY AD3 (C)",
    "className": "SY-AD3",
    "room": "IIOT",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-102",
    "dbId": 102,
    "day": "Friday",
    "startTime": "10:15",
    "endTime": "12:15",
    "displayTime": "10:15 - 12:15",
    "subject": "Sustainable Engineering Practices Lab",
    "facultyId": "FAC-VL",
    "facultyDbId": 10,
    "facultyName": "Dr. Vina Lomte",
    "classDiv": "SY AD3 (B)",
    "className": "SY-AD3",
    "room": "AI1",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-103",
    "dbId": 103,
    "day": "Friday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Sustainable Engineering Practices Lab",
    "facultyId": "FAC-VL",
    "facultyDbId": 10,
    "facultyName": "Dr. Vina Lomte",
    "classDiv": "SY AD3 (C)",
    "className": "SY-AD3",
    "room": "AI1",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-104",
    "dbId": 104,
    "day": "Friday",
    "startTime": "16:15",
    "endTime": "17:15",
    "displayTime": "16:15 - 17:15",
    "subject": "Universal Human Values",
    "facultyId": "FAC-SAK",
    "facultyDbId": 14,
    "facultyName": "Mrs. Shruti A. Kulkarni",
    "classDiv": "SY AD3",
    "className": "SY-AD3",
    "room": "Room 103",
    "batch": null,
    "type": "Tutorial",
    "isLab": false
  },
  {
    "id": "SCH-105",
    "dbId": 105,
    "day": "Monday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Engineering Design and Innovation-I",
    "facultyId": "FAC-ANA",
    "facultyDbId": 7,
    "facultyName": "Mrs. Ashvini N. Ahirrao",
    "classDiv": "TY AD1 (A)",
    "className": "TY-AD1",
    "room": "IOT",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-106",
    "dbId": 106,
    "day": "Monday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Engineering Design and Innovation-I",
    "facultyId": "FAC-ARA",
    "facultyDbId": 23,
    "facultyName": "Ms. Avani Anawardekar",
    "classDiv": "TY AD1 (B)",
    "className": "TY-AD1",
    "room": "AI1",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-107",
    "dbId": 107,
    "day": "Monday",
    "startTime": "08:00",
    "endTime": "10:00",
    "displayTime": "08:00 - 10:00",
    "subject": "Engineering Design and Innovation-I",
    "facultyId": "FAC-DB",
    "facultyDbId": 24,
    "facultyName": "Mrs. Deepali Bhaturkar",
    "classDiv": "TY AD1 (C)",
    "className": "TY-AD1",
    "room": "CN1",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-108",
    "dbId": 108,
    "day": "Monday",
    "startTime": "10:15",
    "endTime": "12:15",
    "displayTime": "10:15 - 12:15",
    "subject": "Artificial Intelligence & Machine Learning Laboratory",
    "facultyId": "FAC-MSA",
    "facultyDbId": 20,
    "facultyName": "Mrs. Mayuri S. Agrawal",
    "classDiv": "TY AD1 (A)",
    "className": "TY-AD1",
    "room": "CN1",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-109",
    "dbId": 109,
    "day": "Monday",
    "startTime": "10:15",
    "endTime": "12:15",
    "displayTime": "10:15 - 12:15",
    "subject": "Computer Network & Cloud Computing Laboratory",
    "facultyId": "FAC-PC",
    "facultyDbId": 21,
    "facultyName": "Mrs. Pooja Chavan",
    "classDiv": "TY AD1 (B)",
    "className": "TY-AD1",
    "room": "Room 609B",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-110",
    "dbId": 110,
    "day": "Monday",
    "startTime": "10:15",
    "endTime": "12:15",
    "displayTime": "10:15 - 12:15",
    "subject": "Edge Computing",
    "facultyId": "FAC-DAG",
    "facultyDbId": 15,
    "facultyName": "Mrs. Dhanashree A. Gore",
    "classDiv": "TY AD1 (C)",
    "className": "TY-AD1",
    "room": "Room 609A",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-111",
    "dbId": 111,
    "day": "Monday",
    "startTime": "13:00",
    "endTime": "14:00",
    "displayTime": "13:00 - 14:00",
    "subject": "Edge Computing / AR & VR",
    "facultyId": "FAC-DAG",
    "facultyDbId": 15,
    "facultyName": "Mrs. Dhanashree A. Gore",
    "classDiv": "TY AD1",
    "className": "TY-AD1",
    "room": "Room 104",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-112",
    "dbId": 112,
    "day": "Monday",
    "startTime": "14:00",
    "endTime": "15:00",
    "displayTime": "14:00 - 15:00",
    "subject": "Sustainable Engineering Practices",
    "facultyId": "FAC-ARA",
    "facultyDbId": 23,
    "facultyName": "Ms. Avani Anawardekar",
    "classDiv": "TY AD1",
    "className": "TY-AD1",
    "room": "Room 104",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-113",
    "dbId": 113,
    "day": "Monday",
    "startTime": "15:15",
    "endTime": "16:15",
    "displayTime": "15:15 - 16:15",
    "subject": "Computer Network & Cloud Computing",
    "facultyId": "FAC-PC",
    "facultyDbId": 21,
    "facultyName": "Mrs. Pooja Chavan",
    "classDiv": "TY AD1",
    "className": "TY-AD1",
    "room": "Room 104",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-114",
    "dbId": 114,
    "day": "Tuesday",
    "startTime": "08:00",
    "endTime": "09:00",
    "displayTime": "08:00 - 09:00",
    "subject": "Computer Network & Cloud Computing",
    "facultyId": "FAC-PC",
    "facultyDbId": 21,
    "facultyName": "Mrs. Pooja Chavan",
    "classDiv": "TY AD1",
    "className": "TY-AD1",
    "room": "Room 102",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-115",
    "dbId": 115,
    "day": "Tuesday",
    "startTime": "09:00",
    "endTime": "10:00",
    "displayTime": "09:00 - 10:00",
    "subject": "Artificial Intelligence & Machine Learning",
    "facultyId": "FAC-MSA",
    "facultyDbId": 20,
    "facultyName": "Mrs. Mayuri S. Agrawal",
    "classDiv": "TY AD1",
    "className": "TY-AD1",
    "room": "Room 102",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-116",
    "dbId": 116,
    "day": "Tuesday",
    "startTime": "10:15",
    "endTime": "11:15",
    "displayTime": "10:15 - 11:15",
    "subject": "Artificial Intelligence & Machine Learning",
    "facultyId": "FAC-MSA",
    "facultyDbId": 20,
    "facultyName": "Mrs. Mayuri S. Agrawal",
    "classDiv": "TY AD1",
    "className": "TY-AD1",
    "room": "Room 104",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-117",
    "dbId": 117,
    "day": "Tuesday",
    "startTime": "11:15",
    "endTime": "12:15",
    "displayTime": "11:15 - 12:15",
    "subject": "Automata Theory and Applications",
    "facultyId": "FAC-GR",
    "facultyDbId": 16,
    "facultyName": "Mrs. Gayatri Rukare",
    "classDiv": "TY AD1",
    "className": "TY-AD1",
    "room": "Room 104",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-118",
    "dbId": 118,
    "day": "Tuesday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Sustainable Engineering Practices Lab",
    "facultyId": "FAC-ARA",
    "facultyDbId": 23,
    "facultyName": "Ms. Avani Anawardekar",
    "classDiv": "TY AD1 (A)",
    "className": "TY-AD1",
    "room": "IIOT",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-119",
    "dbId": 119,
    "day": "Wednesday",
    "startTime": "09:00",
    "endTime": "10:00",
    "displayTime": "09:00 - 10:00",
    "subject": "Computer Network & Cloud Computing",
    "facultyId": "FAC-PC",
    "facultyDbId": 21,
    "facultyName": "Mrs. Pooja Chavan",
    "classDiv": "TY AD1",
    "className": "TY-AD1",
    "room": "Room 104",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-120",
    "dbId": 120,
    "day": "Wednesday",
    "startTime": "10:15",
    "endTime": "12:15",
    "displayTime": "10:15 - 12:15",
    "subject": "Sustainable Engineering Practices",
    "facultyId": "FAC-ARA",
    "facultyDbId": 23,
    "facultyName": "Ms. Avani Anawardekar",
    "classDiv": "TY AD1",
    "className": "TY-AD1",
    "room": "Room 102",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-121",
    "dbId": 121,
    "day": "Wednesday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Computer Network & Cloud Computing Laboratory",
    "facultyId": "FAC-PC",
    "facultyDbId": 21,
    "facultyName": "Mrs. Pooja Chavan",
    "classDiv": "TY AD1 (A)",
    "className": "TY-AD1",
    "room": "CN1",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-122",
    "dbId": 122,
    "day": "Wednesday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Artificial Intelligence & Machine Learning Laboratory",
    "facultyId": "FAC-MSA",
    "facultyDbId": 20,
    "facultyName": "Mrs. Mayuri S. Agrawal",
    "classDiv": "TY AD1 (B)",
    "className": "TY-AD1",
    "room": "AI1",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-123",
    "dbId": 123,
    "day": "Wednesday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Artificial Intelligence & Machine Learning Laboratory",
    "facultyId": "FAC-DB",
    "facultyDbId": 24,
    "facultyName": "Mrs. Deepali Bhaturkar",
    "classDiv": "TY AD1 (C)",
    "className": "TY-AD1",
    "room": "AI2",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-124",
    "dbId": 124,
    "day": "Wednesday",
    "startTime": "15:15",
    "endTime": "16:15",
    "displayTime": "15:15 - 16:15",
    "subject": "Automata Theory and Applications",
    "facultyId": "FAC-GR",
    "facultyDbId": 16,
    "facultyName": "Mrs. Gayatri Rukare",
    "classDiv": "TY AD1",
    "className": "TY-AD1",
    "room": "Room 104",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-125",
    "dbId": 125,
    "day": "Wednesday",
    "startTime": "16:15",
    "endTime": "17:15",
    "displayTime": "16:15 - 17:15",
    "subject": "Automata Theory and Applications",
    "facultyId": "FAC-GR",
    "facultyDbId": 16,
    "facultyName": "Mrs. Gayatri Rukare",
    "classDiv": "TY AD1",
    "className": "TY-AD1",
    "room": "Room 104",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-126",
    "dbId": 126,
    "day": "Thursday",
    "startTime": "10:15",
    "endTime": "12:15",
    "displayTime": "10:15 - 12:15",
    "subject": "Online OEL Lecture",
    "facultyId": "FAC-GR",
    "facultyDbId": 16,
    "facultyName": "Mrs. Gayatri Rukare",
    "classDiv": "TY AD1",
    "className": "TY-AD1",
    "room": "Online",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-127",
    "dbId": 127,
    "day": "Thursday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "AR & VR",
    "facultyId": "FAC-RCY",
    "facultyDbId": 22,
    "facultyName": "Mr. Rishikesh C. Yeolekar",
    "classDiv": "TY AD1 (A)",
    "className": "TY-AD1",
    "room": "ARVR",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-128",
    "dbId": 128,
    "day": "Thursday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Edge Computing",
    "facultyId": "FAC-DAG",
    "facultyDbId": 15,
    "facultyName": "Mrs. Dhanashree A. Gore",
    "classDiv": "TY AD1 (B)",
    "className": "TY-AD1",
    "room": "Room 609A",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-129",
    "dbId": 129,
    "day": "Thursday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Computer Network & Cloud Computing Laboratory",
    "facultyId": "FAC-PC",
    "facultyDbId": 21,
    "facultyName": "Mrs. Pooja Chavan",
    "classDiv": "TY AD1 (C)",
    "className": "TY-AD1",
    "room": "AI2",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-130",
    "dbId": 130,
    "day": "Thursday",
    "startTime": "15:15",
    "endTime": "17:15",
    "displayTime": "15:15 - 17:15",
    "subject": "Engineering Design and Innovation-I",
    "facultyId": "FAC-ARA",
    "facultyDbId": 23,
    "facultyName": "Ms. Avani Anawardekar",
    "classDiv": "TY AD1 (A)",
    "className": "TY-AD1",
    "room": "CN1",
    "batch": "Batch A",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-131",
    "dbId": 131,
    "day": "Thursday",
    "startTime": "15:15",
    "endTime": "17:15",
    "displayTime": "15:15 - 17:15",
    "subject": "Engineering Design and Innovation-I",
    "facultyId": "FAC-SAK",
    "facultyDbId": 14,
    "facultyName": "Mrs. Shruti A. Kulkarni",
    "classDiv": "TY AD1 (B)",
    "className": "TY-AD1",
    "room": "AI1",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-132",
    "dbId": 132,
    "day": "Thursday",
    "startTime": "15:15",
    "endTime": "17:15",
    "displayTime": "15:15 - 17:15",
    "subject": "Engineering Design and Innovation-I",
    "facultyId": "FAC-RCY",
    "facultyDbId": 22,
    "facultyName": "Mr. Rishikesh C. Yeolekar",
    "classDiv": "TY AD1 (C)",
    "className": "TY-AD1",
    "room": "AI2",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-133",
    "dbId": 133,
    "day": "Friday",
    "startTime": "08:00",
    "endTime": "09:00",
    "displayTime": "08:00 - 09:00",
    "subject": "Artificial Intelligence & Machine Learning",
    "facultyId": "FAC-MSA",
    "facultyDbId": 20,
    "facultyName": "Mrs. Mayuri S. Agrawal",
    "classDiv": "TY AD1",
    "className": "TY-AD1",
    "room": "Room 104",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-134",
    "dbId": 134,
    "day": "Friday",
    "startTime": "09:00",
    "endTime": "10:00",
    "displayTime": "09:00 - 10:00",
    "subject": "Edge Computing / AR & VR",
    "facultyId": "FAC-DAG",
    "facultyDbId": 15,
    "facultyName": "Mrs. Dhanashree A. Gore",
    "classDiv": "TY AD1",
    "className": "TY-AD1",
    "room": "Room 104",
    "batch": null,
    "type": "Theory",
    "isLab": false
  },
  {
    "id": "SCH-135",
    "dbId": 135,
    "day": "Friday",
    "startTime": "10:15",
    "endTime": "12:15",
    "displayTime": "10:15 - 12:15",
    "subject": "Sustainable Engineering Practices Lab",
    "facultyId": "FAC-ARA",
    "facultyDbId": 23,
    "facultyName": "Ms. Avani Anawardekar",
    "classDiv": "TY AD1 (B)",
    "className": "TY-AD1",
    "room": "IIOT",
    "batch": "Batch B",
    "type": "Lab Practical",
    "isLab": true
  },
  {
    "id": "SCH-136",
    "dbId": 136,
    "day": "Friday",
    "startTime": "13:00",
    "endTime": "15:00",
    "displayTime": "13:00 - 15:00",
    "subject": "Sustainable Engineering Practices Lab",
    "facultyId": "FAC-ARA",
    "facultyDbId": 23,
    "facultyName": "Ms. Avani Anawardekar",
    "classDiv": "TY AD1 (C)",
    "className": "TY-AD1",
    "room": "IIOT",
    "batch": "Batch C",
    "type": "Lab Practical",
    "isLab": true
  }
];

// Active testing override state (allows testing any day/time without altering system clock)
let simulationOverride = {
  activeDay: null,    // e.g. "Monday", "Tuesday", etc. null = use live system day
  activeTime: null   // e.g. "11:45" (24-hr string), null = use live system time
};

/**
 * Get current academic day name (or simulated day)
 */
function getCurrentAcademicDay() {
  if (simulationOverride.activeDay) {
    return simulationOverride.activeDay;
  }
  const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  return days[new Date().getDay()];
}

/**
 * Get current time string in HH:MM 24-hr format (or simulated time)
 */
function getCurrentAcademicTime() {
  if (simulationOverride.activeTime) {
    return simulationOverride.activeTime;
  }
  const now = new Date();
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  return `${hours}:${minutes}`;
}

/**
 * Get formatted current date string (e.g. "Monday, October 18, 2026")
 */
function getFormattedAcademicDate() {
  const now = new Date();
  const dayName = getCurrentAcademicDay();
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  const dateStr = now.toLocaleDateString('en-US', options);
  return `${dayName}, ${dateStr}`;
}

/**
 * Returns all lectures for a given day (across all faculty/classes)
 */
function getMasterLecturesForDay(dayName) {
  return MASTER_TIMETABLE.filter(item => item.day.toLowerCase() === dayName.toLowerCase());
}

/**
 * Returns lectures for a specific faculty member on a given day
 */
function getFacultyLecturesForDay(facultyId, dayName) {
  if (!facultyId || !dayName) return [];
  const target = String(facultyId).trim().toUpperCase();
  return MASTER_TIMETABLE.filter(item => {
    const mId = String(item.facultyId || item.faculty_id || '').trim().toUpperCase();
    const matchesFac = (
      mId === target ||
      String(item.facultyDbId) === target ||
      String(item.faculty_id) === target
    );
    const matchesDay = item.day && item.day.toLowerCase() === dayName.toLowerCase();
    return matchesFac && matchesDay;
  });
}

/**
 * Calculate dynamic status: "Ongoing", "Upcoming", or "Completed"
 */
function computeLectureStatus(startTimeStr, endTimeStr, currentTimeStr) {
  const current = currentTimeStr || getCurrentAcademicTime();
  if (current < startTimeStr) {
    return "Upcoming";
  } else if (current >= startTimeStr && current < endTimeStr) {
    return "Ongoing";
  } else {
    return "Completed";
  }
}

/**
 * Returns the immediate next or currently ongoing lecture
 */
function findNextLecture(lectures) {
  const current = getCurrentAcademicTime();
  // 1. Check for ongoing lecture
  const ongoing = lectures.find(l => current >= l.startTime && current < l.endTime);
  if (ongoing) return { lecture: ongoing, status: "Ongoing" };

  // 2. Otherwise find the first upcoming lecture
  const upcoming = lectures.filter(l => l.startTime > current).sort((a, b) => a.startTime.localeCompare(b.startTime));
  if (upcoming.length > 0) return { lecture: upcoming[0], status: "Upcoming" };

  return null;
}

// =============================================================================
// MASTER FACULTY ROSTER
// =============================================================================
const MASTER_FACULTY_LIST = [
  {
    "id": "FAC-ANA",
    "dbId": 7,
    "name": "Mrs. Ashvini N. Ahirrao",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Assistant Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "ana@edunova.edu",
    "maxHours": 16,
    "role": "faculty"
  },
  {
    "id": "FAC-101",
    "dbId": 2,
    "name": "Mrs. Ashvini N. Ahirrao",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "sharma@edunova.edu",
    "maxHours": 16
  },
  {
    "id": "FAC-102",
    "dbId": 3,
    "name": "Prof. Patil",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Assistant Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "patil@edunova.edu",
    "maxHours": 16
  },
  {
    "id": "FAC-103",
    "dbId": 4,
    "name": "Prof. Joshi",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Assistant Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "joshi@edunova.edu",
    "maxHours": 16
  },
  {
    "id": "FAC-104",
    "dbId": 5,
    "name": "Dr. Kulkarni",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "kulkarni@edunova.edu",
    "maxHours": 16
  },
  {
    "id": "FAC-105",
    "dbId": 6,
    "name": "Prof. Pawar",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Assistant Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "pawar@edunova.edu",
    "maxHours": 16
  },
  {
    "id": "FAC-ANA",
    "dbId": 7,
    "name": "Mrs. Ashvini N. Ahirrao",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Assistant Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "ana@edunova.edu",
    "maxHours": 18
  },
  {
    "id": "FAC-ASS",
    "dbId": 8,
    "name": "Mrs. Abhilasha S. Shinde",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Assistant Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "ass@edunova.edu",
    "maxHours": 18
  },
  {
    "id": "FAC-SJN",
    "dbId": 9,
    "name": "Mrs. Sinu J. Nambiar",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Assistant Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "sjn@edunova.edu",
    "maxHours": 18
  },
  {
    "id": "FAC-VL",
    "dbId": 10,
    "name": "Dr. Vina Lomte",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "vl@edunova.edu",
    "maxHours": 18
  },
  {
    "id": "FAC-MKM",
    "dbId": 11,
    "name": "Dr. M. K. Mokashi",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "mkm@edunova.edu",
    "maxHours": 18
  },
  {
    "id": "FAC-SDJ",
    "dbId": 12,
    "name": "Mrs. Swati D. Jakkan",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Assistant Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "sdj@edunova.edu",
    "maxHours": 18
  },
  {
    "id": "FAC-KPS",
    "dbId": 13,
    "name": "Mrs. Kalpna P. Saharan",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Assistant Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "kps@edunova.edu",
    "maxHours": 18
  },
  {
    "id": "FAC-SAK",
    "dbId": 14,
    "name": "Mrs. Shruti A. Kulkarni",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Assistant Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "sak@edunova.edu",
    "maxHours": 18
  },
  {
    "id": "FAC-DAG",
    "dbId": 15,
    "name": "Mrs. Dhanashree A. Gore",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Assistant Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "dag@edunova.edu",
    "maxHours": 18
  },
  {
    "id": "FAC-GR",
    "dbId": 16,
    "name": "Mrs. Gayatri Rukare",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Assistant Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "gr@edunova.edu",
    "maxHours": 18
  },
  {
    "id": "FAC-SDK",
    "dbId": 17,
    "name": "Mrs. Supriya D. Kapase",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Assistant Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "sdk@edunova.edu",
    "maxHours": 16
  },
  {
    "id": "FAC-MK",
    "dbId": 18,
    "name": "Dr. Mrunal Kothari",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "mk@edunova.edu",
    "maxHours": 16
  },
  {
    "id": "FAC-DRD",
    "dbId": 19,
    "name": "Dr. Dhanraj R. Dhotre",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "drdhotre@edunova.edu",
    "maxHours": 18
  },
  {
    "id": "FAC-MSA",
    "dbId": 20,
    "name": "Mrs. Mayuri S. Agrawal",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Assistant Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "msa@edunova.edu",
    "maxHours": 18
  },
  {
    "id": "FAC-PC",
    "dbId": 21,
    "name": "Mrs. Pooja Chavan",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Assistant Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "pc@edunova.edu",
    "maxHours": 18
  },
  {
    "id": "FAC-RCY",
    "dbId": 22,
    "name": "Mr. Rishikesh C. Yeolekar",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Assistant Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "rcy@edunova.edu",
    "maxHours": 16
  },
  {
    "id": "FAC-ARA",
    "dbId": 23,
    "name": "Ms. Avani Anawardekar",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Assistant Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "ara@edunova.edu",
    "maxHours": 18
  },
  {
    "id": "FAC-DB",
    "dbId": 24,
    "name": "Mrs. Deepali Bhaturkar",
    "dept": "Artificial Intelligence and Data Science (AI&DS)",
    "designation": "Assistant Professor",
    "classes": [
      "SY AD1",
      "SY AD2",
      "SY AD3",
      "TY AD1"
    ],
    "email": "db@edunova.edu",
    "maxHours": 16
  }
];

// Helper to get authenticated faculty ID with privacy enforcement
function getAuthenticatedFacultyId() {
  try {
    const rawAuth = localStorage.getItem("edunova_auth_user");
    if (rawAuth) {
      const authObj = JSON.parse(rawAuth);
      // Prioritize alphanumeric faculty code (e.g. FAC-ANA, FAC-DRD, FAC-101)
      if (authObj) {
        return authObj.faculty_id || authObj.facultyId || authObj.id || authObj.email;
      }
    }
  } catch (e) {}
  return localStorage.getItem("edunova_active_faculty_id") || EDUNOVA_FACULTY_ID;
}

function getActiveFacultyId() {
  return getAuthenticatedFacultyId();
}

function setActiveFacultyId(id) {
  const authId = getAuthenticatedFacultyId();
  // Privacy enforcement: Prevent switching to or accessing another faculty's data
  if (id && id !== authId) {
    console.warn("Access denied: You are only authorized to access your own faculty data.");
    return false;
  }
  localStorage.setItem("edunova_active_faculty_id", authId);
  return true;
}


function getTeachingFacultyList() {
  return MASTER_FACULTY_LIST.filter(f => f.role !== 'admin' && f.id !== 'ADM-101');
}

function getActiveFaculty() {
  const activeId = getActiveFacultyId();
  if (!activeId) return MASTER_FACULTY_LIST[0];
  const target = String(activeId).trim().toUpperCase();
  const found = MASTER_FACULTY_LIST.find(f => {
    return (
      (f.id && String(f.id).trim().toUpperCase() === target) ||
      (f.dbId && String(f.dbId) === target) ||
      (f.email && String(f.email).trim().toUpperCase() === target)
    );
  });
  return found || MASTER_FACULTY_LIST[0];
}

// =============================================================================
// REPLACEMENT REQUESTS ENGINE (SHARED VIA LOCALSTORAGE)
// =============================================================================
const REPLACEMENT_STORAGE_KEY = "edunova_replacement_requests_v2";

const DEFAULT_REPLACEMENT_REQUESTS = [];

function getReplacementRequests() {
  try {
    const raw = localStorage.getItem(REPLACEMENT_STORAGE_KEY);
    if (!raw) {
      localStorage.setItem(REPLACEMENT_STORAGE_KEY, JSON.stringify(DEFAULT_REPLACEMENT_REQUESTS));
      return DEFAULT_REPLACEMENT_REQUESTS;
    }
    return JSON.parse(raw);
  } catch (e) {
    return DEFAULT_REPLACEMENT_REQUESTS;
  }
}

function saveReplacementRequests(requests) {
  localStorage.setItem(REPLACEMENT_STORAGE_KEY, JSON.stringify(requests));
}

/**
 * Check if a faculty member has an overlapping slot on a given day/time
 */
function checkFacultySlotConflict(facultyId, day, startTime, endTime) {
  const dayLectures = getFacultyLecturesForDay(facultyId, day);
  return dayLectures.find(l => {
    // Overlap condition: not strictly before and not strictly after
    return !(l.endTime <= startTime || l.startTime >= endTime);
  });
}

/**
 * Get eligible replacement faculty members for a given slot
 * Evaluates real-time availability and smart recommendations (same dept & same class)
 */
function getEligibleReplacementFaculty(requesterId, day, startTime, endTime, classDiv) {
  const requester = MASTER_FACULTY_LIST.find(f => f.id === requesterId);
  const requesterDept = requester ? requester.dept : "Artificial Intelligence and Data Science (AI&DS)";

  // Extract cohort/class keywords, e.g. "TY AI&DS", "SY AI&DS", "BE AI&DS"
  const classKeywords = classDiv ? classDiv.split(" - ")[0].trim() : "";

  return MASTER_FACULTY_LIST
    .filter(f => f.id !== requesterId)
    .map(faculty => {
      const conflict = checkFacultySlotConflict(faculty.id, day, startTime, endTime);
      const isAvailable = !conflict;
      const isSameDept = faculty.dept === requesterDept;
      const teachesSameClass = faculty.classes.some(c => c.includes(classKeywords) || classKeywords.includes(c.split(" - ")[0]));

      let isRecommended = false;
      let recommendationReason = "";

      if (isAvailable && isSameDept && teachesSameClass) {
        isRecommended = true;
        recommendationReason = `Same Department & Teaches ${classKeywords}`;
      } else if (isAvailable && isSameDept) {
        recommendationReason = "Same Department Specialist";
      }

      return {
        faculty,
        isAvailable,
        isRecommended,
        recommendationReason,
        conflictDetails: conflict ? `${conflict.subject} (${conflict.room}, ${conflict.displayTime})` : null
      };
    })
    .sort((a, b) => {
      // 1. Recommended & Available first
      if (a.isRecommended && !b.isRecommended) return -1;
      if (!a.isRecommended && b.isRecommended) return 1;
      // 2. Available first
      if (a.isAvailable && !b.isAvailable) return -1;
      if (!a.isAvailable && b.isAvailable) return 1;
      // 3. Alphabetical
      return a.faculty.name.localeCompare(b.faculty.name);
    });
}

/**
 * Create a new replacement request
 */
function createReplacementRequest(data) {
  const requests = getReplacementRequests();
  const newId = `REQ-2026-${Math.floor(100 + Math.random() * 900)}`;

  const newRequest = {
    id: newId,
    requestingFacultyId: data.requestingFacultyId,
    requestingFacultyName: data.requestingFacultyName,
    targetFacultyId: data.targetFacultyId,
    targetFacultyName: data.targetFacultyName,
    lectureId: data.lectureId,
    day: data.day,
    date: data.date,
    startTime: data.startTime,
    endTime: data.endTime,
    displayTime: data.displayTime,
    subject: data.subject,
    classDiv: data.classDiv,
    room: data.room,
    reason: data.reason || "Academic substitution request",
    status: "Pending",
    createdAt: new Date().toISOString()
  };

  requests.unshift(newRequest);
  saveReplacementRequests(requests);

  // Send notification to target faculty
  addNotification({
    recipientId: data.targetFacultyId,
    title: "New Peer Replacement Request",
    message: `${data.requestingFacultyName} requested you to cover ${data.subject} (${data.classDiv}) on ${data.day} ${data.displayTime}.`,
    type: "request_received",
    relatedRequestId: newId
  });

  return { success: true, request: newRequest };
}

/**
 * Update request status (Accept / Reject) with clash verification
 */
function updateReplacementRequestStatus(requestId, newStatus, respondingFacultyId) {
  const requests = getReplacementRequests();
  const reqIndex = requests.findIndex(r => r.id === requestId);

  if (reqIndex === -1) {
    return { success: false, error: "Request not found." };
  }

  const req = requests[reqIndex];

  // Prevent responding to own request
  if (req.requestingFacultyId === respondingFacultyId) {
    return { success: false, error: "Faculty cannot respond to their own request." };
  }

  // If accepting, prevent if receiving faculty has a time clash
  if (newStatus === "Accepted") {
    const clash = checkFacultySlotConflict(respondingFacultyId, req.day, req.startTime, req.endTime);
    if (clash) {
      return {
        success: false,
        error: `Schedule Clash Detected: You already have "${clash.subject}" scheduled in ${clash.room} from ${clash.displayTime}. You cannot accept this slot.`
      };
    }
  }

  req.status = newStatus;
  req.respondedAt = new Date().toISOString();
  saveReplacementRequests(requests);

  // Notify the requesting faculty
  const statusLabel = newStatus === "Accepted" ? "Accepted" : "Declined";
  addNotification({
    recipientId: req.requestingFacultyId,
    title: `Replacement Request ${statusLabel}`,
    message: `${req.targetFacultyName} has ${statusLabel.toLowerCase()} your substitution request for ${req.subject} on ${req.day}.`,
    type: newStatus === "Accepted" ? "request_accepted" : "request_rejected",
    relatedRequestId: req.id
  });

  return { success: true, request: req };
}

/**
 * Cancel a pending replacement request (by requester only)
 */
function cancelReplacementRequest(requestId, facultyId) {
  const requests = getReplacementRequests();
  const req = requests.find(r => r.id === requestId);

  if (!req) return { success: false, error: "Request not found." };
  if (req.requestingFacultyId !== facultyId) {
    return { success: false, error: "Only the requesting faculty member can cancel this request." };
  }
  if (req.status !== "Pending") {
    return { success: false, error: `Cannot cancel a request that is already ${req.status}.` };
  }

  req.status = "Cancelled";
  req.cancelledAt = new Date().toISOString();
  saveReplacementRequests(requests);

  // Notify target faculty of cancellation
  addNotification({
    recipientId: req.targetFacultyId,
    title: "Replacement Request Cancelled",
    message: `${req.requestingFacultyName} cancelled the substitution request for ${req.subject} on ${req.day}.`,
    type: "request_cancelled",
    relatedRequestId: req.id
  });

  return { success: true, request: req };
}

// =============================================================================
// NOTIFICATION SYSTEM (SHARED VIA LOCALSTORAGE)
// =============================================================================
const NOTIFICATION_STORAGE_KEY = "edunova_notifications_v2";

const DEFAULT_NOTIFICATIONS = [];

function getNotifications(recipientId) {
  try {
    const raw = localStorage.getItem(NOTIFICATION_STORAGE_KEY);
    const all = raw ? JSON.parse(raw) : JSON.parse(JSON.stringify(DEFAULT_NOTIFICATIONS));
    if (!raw) localStorage.setItem(NOTIFICATION_STORAGE_KEY, JSON.stringify(DEFAULT_NOTIFICATIONS));
    if (!recipientId) return all;
    return all.filter(n => n.recipientId === recipientId || n.recipientId === "all");
  } catch (e) {
    return DEFAULT_NOTIFICATIONS;
  }
}

function addNotification(item) {
  try {
    const raw = localStorage.getItem(NOTIFICATION_STORAGE_KEY);
    const all = raw ? JSON.parse(raw) : JSON.parse(JSON.stringify(DEFAULT_NOTIFICATIONS));
    const newNotif = {
      id: `NOTIF-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
      recipientId: item.recipientId,
      title: item.title,
      message: item.message,
      type: item.type || "info",
      isRead: false,
      timestamp: new Date().toISOString(),
      relatedRequestId: item.relatedRequestId || null,
      workDetails: item.workDetails || null
    };
    all.unshift(newNotif);
    localStorage.setItem(NOTIFICATION_STORAGE_KEY, JSON.stringify(all));
    return newNotif;
  } catch (e) {
    console.error(e);
  }
}

function markNotificationRead(notifId) {
  try {
    const raw = localStorage.getItem(NOTIFICATION_STORAGE_KEY);
    const all = raw ? JSON.parse(raw) : DEFAULT_NOTIFICATIONS;
    const item = all.find(n => n.id === notifId);
    if (item) {
      item.isRead = true;
      localStorage.setItem(NOTIFICATION_STORAGE_KEY, JSON.stringify(all));
    }
  } catch (e) {
    console.error(e);
  }
}

function getUnreadNotificationCount(recipientId) {
  const notifs = getNotifications(recipientId);
  return notifs.filter(n => !n.isRead).length;
}

// =============================================================================
// FACULTY WORKLOAD ANALYTICS ENGINE (FOR POWER BI & DATA EXPORT)
// =============================================================================
const BENCHMARK_WEEKLY_HOURS = 18; // Standard academic maximum teaching benchmark

/**
 * Calculate weekly workload metrics per faculty from MASTER_TIMETABLE
 */
function calculateFacultyWorkloadData() {
  return MASTER_FACULTY_LIST.map(faculty => {
    // Find all timetable slots assigned to this faculty
    const slots = MASTER_TIMETABLE.filter(item => item.facultyId === faculty.id);

    // Sum duration in decimal hours
    let totalHours = 0;
    slots.forEach(slot => {
      const [sh, sm] = slot.startTime.split(":").map(Number);
      const [eh, em] = slot.endTime.split(":").map(Number);
      const duration = (eh + em / 60) - (sh + sm / 60);
      totalHours += duration;
    });

    // Round to 1 decimal place
    totalHours = Math.round(totalHours * 10) / 10;
    const workloadPercentage = Math.round((totalHours / BENCHMARK_WEEKLY_HOURS) * 100);

    let workloadCategory = "Normal";
    if (totalHours < 14) workloadCategory = "Low";
    else if (totalHours > 18) workloadCategory = "High";

    return {
      facultyId: faculty.id,
      facultyName: faculty.name,
      department: faculty.dept,
      designation: faculty.designation,
      assignedLectures: slots.length,
      weeklyHours: totalHours,
      workloadPercentage: workloadPercentage,
      workloadCategory: workloadCategory // "Low" | "Normal" | "High"
    };
  });
}

/**
 * Generate CSV dataset ready to import directly into Power BI Desktop
 */
function generateWorkloadCSV() {
  const data = calculateFacultyWorkloadData();
  const headers = ["Faculty_ID", "Faculty_Name", "Department", "Designation", "Assigned_Lectures", "Weekly_Working_Hours", "Workload_Percentage", "Workload_Category"];
  
  const rows = data.map(d => [
    `"${d.facultyId}"`,
    `"${d.facultyName}"`,
    `"${d.department}"`,
    `"${d.designation}"`,
    d.assignedLectures,
    d.weeklyHours,
    d.workloadPercentage,
    `"${d.workloadCategory}"`
  ]);

  return [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
}

/**
 * Trigger browser download of Power BI ready CSV
 */
function downloadWorkloadCSV() {
  const csvContent = generateWorkloadCSV();
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", `edunova_faculty_workload_powerbi_${new Date().toISOString().split("T")[0]}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Power BI Embed Configuration Persistence
const POWERBI_CONFIG_KEY = "edunova_powerbi_embed_config";

function getPowerBIEmbedConfig() {
  try {
    const raw = localStorage.getItem(POWERBI_CONFIG_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

function savePowerBIEmbedConfig(embedUrl, reportName) {
  const config = {
    embedUrl: embedUrl.trim(),
    reportName: reportName || "Faculty Workload Analytics",
    connectedAt: new Date().toISOString()
  };
  localStorage.setItem(POWERBI_CONFIG_KEY, JSON.stringify(config));
  return config;
}

function clearPowerBIEmbedConfig() {
  localStorage.removeItem(POWERBI_CONFIG_KEY);
}

// =============================================================================
// DEPARTMENT ROOMS & FACILITIES MODEL (CLASSROOMS & LABORATORIES)
// =============================================================================
const DEPARTMENT_ROOMS = {
  classrooms: [
    { id: "Room 102", name: "Room 102", type: "Classroom" },
    { id: "Room 103", name: "Room 103", type: "Classroom" },
    { id: "Room 104", name: "Room 104", type: "Classroom" }
  ],
  laboratories: [
    { id: "Lab 609A", name: "Lab 609A", type: "Laboratory" },
    { id: "Lab 609B", name: "Lab 609B", type: "Laboratory" },
    { id: "AI1", name: "AI1", type: "Lab 607 Sub-lab (AI1)" },
    { id: "AI2", name: "AI2", type: "Lab 607 Sub-lab (AI2)" },
    { id: "CN1", name: "CN1", type: "Lab 607 Sub-lab (CN1)" },
    { id: "ARVR", name: "ARVR", type: "Lab 607 Sub-lab (ARVR)" },
    { id: "IIOT", name: "IIOT", type: "Lab 607 Sub-lab (IIOT)" }
  ]
};

const ACADEMIC_PERIODS = [
  { period: 1, startTime: "08:00", endTime: "09:00", label: "08:00 AM – 09:00 AM" },
  { period: 2, startTime: "09:00", endTime: "10:00", label: "09:00 AM – 10:00 AM" },
  { period: "Break 1", startTime: "10:00", endTime: "10:15", label: "10:00 AM – 10:15 AM (Morning Break)", isBreak: true },
  { period: 3, startTime: "10:15", endTime: "11:15", label: "10:15 AM – 11:15 AM" },
  { period: 4, startTime: "11:15", endTime: "12:15", label: "11:15 AM – 12:15 PM" },
  { period: "Lunch", startTime: "12:15", endTime: "13:00", label: "12:15 PM – 01:00 PM (Lunch Break)", isBreak: true },
  { period: 5, startTime: "13:00", endTime: "14:00", label: "01:00 PM – 02:00 PM" },
  { period: 6, startTime: "14:00", endTime: "15:00", label: "02:00 PM – 03:00 PM" },
  { period: "Break 2", startTime: "15:00", endTime: "15:15", label: "03:00 PM – 03:15 PM (Afternoon Break)", isBreak: true },
  { period: 7, startTime: "15:15", endTime: "16:15", label: "03:15 PM – 04:15 PM" },
  { period: 8, startTime: "16:15", endTime: "17:15", label: "04:15 PM – 05:15 PM" }
];

// Check if a room is occupied on a day and time interval with strict overlap & conflict detection
function getRoomOccupancy(roomId, day, startTime, endTime) {
  const target = String(roomId || '').trim().toLowerCase();
  const daySlots = MASTER_TIMETABLE.filter(s => {
    if (s.day !== day) return false;
    const sRoom = String(s.room || '').trim().toLowerCase();
    return sRoom === target ||
      sRoom.replace(/^room\s*/, '') === target.replace(/^room\s*/, '') ||
      sRoom.replace(/^lab\s*/, '') === target.replace(/^lab\s*/, '');
  });

  // Strict interval overlap: start1 < end2 AND start2 < end1
  const overlappingSessions = daySlots.filter(s => {
    const sStart = s.startTime || s.start_time;
    const sEnd = s.endTime || s.end_time;
    if (!sStart || !sEnd) return false;
    return (startTime < sEnd) && (sStart < endTime);
  });

  const isOccupied = overlappingSessions.length > 0;
  const hasConflict = overlappingSessions.length > 1;

  return {
    isOccupied,
    hasConflict,
    session: overlappingSessions[0] || null,
    sessions: overlappingSessions
  };
}

// Calculate real-time faculty availability for a day and slot from timetable
function getFacultyAvailabilityForSlot(day, startTime, endTime) {
  const workloadList = calculateFacultyWorkloadData();
  const availableFaculty = [];
  const occupiedFaculty = [];

  MASTER_FACULTY_LIST.forEach(faculty => {
    const conflictSlot = checkFacultySlotConflict(faculty.id, day, startTime, endTime);
    const wk = workloadList.find(w => w.facultyId === faculty.id) || {
      weeklyHours: 0,
      assignedLectures: 0,
      workloadPercentage: 0,
      workloadCategory: "Normal"
    };

    if (conflictSlot) {
      occupiedFaculty.push({
        ...faculty,
        isAvailable: false,
        occupiedSlot: conflictSlot,
        workload: wk
      });
    } else {
      availableFaculty.push({
        ...faculty,
        isAvailable: true,
        availableTimeSlot: `${startTime} – ${endTime}`,
        workload: wk
      });
    }
  });

  return {
    day,
    startTime,
    endTime,
    availableFaculty,
    occupiedFaculty
  };
}

// Get day schedule breakdown for a faculty member showing occupied and free periods
function getFacultyDaySchedule(facultyId, day) {
  const daySlots = MASTER_TIMETABLE.filter(s => s.facultyId === facultyId && s.day === day);
  
  return ACADEMIC_PERIODS.map(period => {
    const occupiedSlot = daySlots.find(s => {
      return !(s.endTime <= period.startTime || s.startTime >= period.endTime);
    });

    return {
      ...period,
      isOccupied: !!occupiedSlot,
      session: occupiedSlot || null
    };
  });
}

// Get comprehensive faculty workload metrics
function getFacultyWorkloadDetailed(facultyId) {
  const target = String(facultyId || '').trim().toUpperCase();
  const faculty = MASTER_FACULTY_LIST.find(f => {
    return (
      (f.id && String(f.id).trim().toUpperCase() === target) ||
      (f.dbId && String(f.dbId) === target) ||
      (f.email && String(f.email).trim().toUpperCase() === target)
    );
  }) || (typeof getActiveFaculty === 'function' ? getActiveFaculty() : MASTER_FACULTY_LIST[0]);
  const fid = faculty ? faculty.id : target;
  const fDbId = faculty ? faculty.dbId : null;
  const slots = MASTER_TIMETABLE.filter(s => {
    const sId = String(s.facultyId || s.faculty_id || '').trim().toUpperCase();
    return sId === String(fid).toUpperCase() || (fDbId && (s.facultyDbId === fDbId || s.faculty_id === fDbId));
  });

  let totalHours = 0;
  let theoryHours = 0;
  let practicalHours = 0;
  let theoryCount = 0;
  let practicalCount = 0;

  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  const dayBreakdown = {};
  days.forEach(d => {
    dayBreakdown[d] = { hours: 0, theoryCount: 0, practicalCount: 0, sessions: [] };
  });

  slots.forEach(slot => {
    const [sh, sm] = slot.startTime.split(":").map(Number);
    const [eh, em] = slot.endTime.split(":").map(Number);
    const duration = (eh + em / 60) - (sh + sm / 60);

    totalHours += duration;
    const isTheory = slot.type === "Theory";
    if (isTheory) {
      theoryHours += duration;
      theoryCount++;
    } else {
      practicalHours += duration;
      practicalCount++;
    }

    if (dayBreakdown[slot.day]) {
      dayBreakdown[slot.day].hours += duration;
      if (isTheory) dayBreakdown[slot.day].theoryCount++;
      else dayBreakdown[slot.day].practicalCount++;
      dayBreakdown[slot.day].sessions.push(slot);
    }
  });

  totalHours = Math.round(totalHours * 10) / 10;
  theoryHours = Math.round(theoryHours * 10) / 10;
  practicalHours = Math.round(practicalHours * 10) / 10;

  let category = "Normal";
  if (totalHours < 14) category = "Low";
  else if (totalHours > 18) category = "High";

  return {
    faculty,
    totalHours,
    theoryHours,
    practicalHours,
    theoryCount,
    practicalCount,
    totalSessions: slots.length,
    workloadPercentage: Math.round((totalHours / 16) * 100),
    category,
    dayBreakdown,
    slots
  };
}

// Power BI CSV export for Room & Laboratory Facility Utilization
function generateRoomsUtilizationPowerBICSV() {
  const headers = ["Room_ID", "Room_Name", "Room_Type", "Capacity", "Day", "Slot_Time", "Status", "Occupied_By_Class", "Subject", "Faculty_Name"];
  const rows = [];
  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  const allRooms = [...DEPARTMENT_ROOMS.classrooms, ...DEPARTMENT_ROOMS.laboratories];

  days.forEach(day => {
    ACADEMIC_PERIODS.forEach(period => {
      allRooms.forEach(room => {
        const occ = getRoomOccupancy(room.id, day, period.startTime, period.endTime);
        rows.push([
          `"${room.id}"`,
          `"${room.name}"`,
          `"${room.type}"`,
          room.capacity,
          `"${day}"`,
          `"${period.label}"`,
          `"${occ.isOccupied ? 'Occupied' : 'Available'}"`,
          `"${occ.isOccupied ? occ.session.classDiv : '-'}"`,
          `"${occ.isOccupied ? occ.session.subject : '-'}"`,
          `"${occ.isOccupied ? occ.session.facultyName : '-'}"`
        ]);
      });
    });
  });

  return [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
}

function downloadRoomsUtilizationPowerBICSV() {
  const csvContent = generateRoomsUtilizationPowerBICSV();
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", `edunova_room_utilization_powerbi_${new Date().toISOString().split("T")[0]}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Storage for Admin Faculty Duty Assignments
const FACULTY_DUTY_STORAGE_KEY = "edunova_faculty_duty_assignments_v1";

function getFacultyDutyAssignments(facultyId) {
  try {
    const raw = localStorage.getItem(FACULTY_DUTY_STORAGE_KEY);
    const all = raw ? JSON.parse(raw) : [];
    if (!facultyId) return all;
    return all.filter(a => a.facultyId === facultyId || (a.facultyId && a.facultyId.toUpperCase() === facultyId.toUpperCase()));
  } catch (e) {
    return [];
  }
}

function assignFacultyDuty(assignment) {
  try {
    const current = getFacultyDutyAssignments();
    const isConflict = current.some(a => 
      a.facultyId === assignment.facultyId &&
      a.day === assignment.day &&
      a.timeSlot === assignment.timeSlot
    );
    if (isConflict) {
      return { success: false, error: "Faculty is already assigned to a duty at this time slot." };
    }
    const newEntry = {
      id: `DUTY-${Date.now()}`,
      facultyId: assignment.facultyId,
      facultyName: assignment.facultyName,
      department: assignment.department,
      day: assignment.day,
      timeSlot: assignment.timeSlot,
      dutyType: assignment.dutyType,
      venue: assignment.venue || "Campus",
      notes: assignment.notes || "",
      assignedAt: new Date().toISOString()
    };
    current.unshift(newEntry);
    localStorage.setItem(FACULTY_DUTY_STORAGE_KEY, JSON.stringify(current));

    // Automatically create a notification specifically for this assigned faculty member
    try {
      addNotification({
        recipientId: assignment.facultyId,
        title: `New Duty Assigned: ${assignment.dutyType}`,
        message: `Admin / HOD has assigned you to ${assignment.dutyType} on ${assignment.day} (${assignment.timeSlot}) at ${assignment.venue || "Campus"}.`,
        type: "work_assigned",
        workDetails: {
          taskTitle: `${assignment.dutyType} Duty`,
          category: "Faculty Duty Assignment",
          assignedBy: "Admin / HOD",
          assignedDate: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
          deadline: `${assignment.day} (${assignment.timeSlot})`,
          venue: assignment.venue || "Campus",
          status: "Assigned",
          priority: "High",
          notes: assignment.notes || `Assigned to ${assignment.dutyType} on ${assignment.day} during ${assignment.timeSlot}.`
        }
      });
    } catch (notifErr) {
      console.error("Failed to dispatch duty notification:", notifErr);
    }

    return { success: true, assignment: newEntry };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

// =============================================================================
// COURSE SYLLABUS PLANNING & TRACKING ENGINE (PER-DIVISION ISOLATION)
// =============================================================================
const SYLLABUS_STORAGE_KEY = "edunova_syllabus_progress_v4";
const LECTURE_LOG_STORAGE_KEY = "edunova_lecture_activity_logs_v4";

// Template syllabi for subjects (THEORY and PRACTICAL/LAB ONLY - NO TUTORIALS)
const DEFAULT_SYLLABUS_TEMPLATES = {
  "Operating Systems": {
    "Theory": [
      {
        unitId: "OST-U1",
        unitNumber: 1,
        unitTitle: "Overview of Operating Systems & System Calls",
        topics: [
          { id: "OST-1.1", order: 1, name: "OS Structures, Dual-Mode Operation & Kernel Architectures", plannedLectures: 2, completedLectures: 2, targetDate: "2026-08-10", status: "Completed" },
          { id: "OST-1.2", order: 2, name: "System Calls, API & OS Services Interface", plannedLectures: 2, completedLectures: 2, targetDate: "2026-08-18", status: "Completed" },
          { id: "OST-1.3", order: 3, name: "Operating System Booting & System Programs", plannedLectures: 2, completedLectures: 2, targetDate: "2026-08-25", status: "Completed" }
        ]
      },
      {
        unitId: "OST-U2",
        unitNumber: 2,
        unitTitle: "Process Management & CPU Scheduling",
        topics: [
          { id: "OST-2.1", order: 4, name: "Process Concept, PCB, Context Switching & Operations", plannedLectures: 2, completedLectures: 2, targetDate: "2026-09-02", status: "Completed" },
          { id: "OST-2.2", order: 5, name: "Inter-Process Communication (Shared Memory & Message Passing)", plannedLectures: 2, completedLectures: 2, targetDate: "2026-09-10", status: "Completed" },
          { id: "OST-2.3", order: 6, name: "CPU Scheduling Criteria & Algorithms (FCFS, SJF, Round Robin)", plannedLectures: 4, completedLectures: 4, targetDate: "2026-09-20", status: "Completed" }
        ]
      },
      {
        unitId: "OST-U3",
        unitNumber: 3,
        unitTitle: "Process Synchronization & Deadlocks",
        topics: [
          { id: "OST-3.1", order: 7, name: "Critical-Section Problem, Peterson's Algorithm & Mutex Locks", plannedLectures: 3, completedLectures: 3, targetDate: "2026-09-28", status: "Completed" },
          { id: "OST-3.2", order: 8, name: "Semaphores & Classical Synchronization Problems", plannedLectures: 2, completedLectures: 2, targetDate: "2026-10-04", status: "Completed" },
          { id: "OST-3.3", order: 9, name: "Deadlock Characterization, Prevention, Avoidance & Banker's Algorithm", plannedLectures: 3, completedLectures: 3, targetDate: "2026-10-12", status: "Completed" }
        ]
      },
      {
        unitId: "OST-U4",
        unitNumber: 4,
        unitTitle: "Memory Management & Virtual Memory",
        topics: [
          { id: "OST-4.1", order: 10, name: "Contiguous Memory Allocation, Fragmentation & Paging Hardware", plannedLectures: 3, completedLectures: 3, targetDate: "2026-10-16", status: "Completed" },
          { id: "OST-4.2", order: 11, name: "Virtual Memory, Demand Paging & Page Replacement Algorithms", plannedLectures: 3, completedLectures: 2, targetDate: "2026-10-22", status: "Ongoing" },
          { id: "OST-4.3", order: 12, name: "Thrashing, Working Set Model & Page Fault Handling", plannedLectures: 2, completedLectures: 0, targetDate: "2026-10-28", status: "Pending" }
        ]
      },
      {
        unitId: "OST-U5",
        unitNumber: 5,
        unitTitle: "Storage Management & File Systems",
        topics: [
          { id: "OST-5.1", order: 13, name: "File Concept, Access Methods, Directory & Mounting", plannedLectures: 3, completedLectures: 0, targetDate: "2026-11-06", status: "Pending" },
          { id: "OST-5.2", order: 14, name: "Disk Scheduling Algorithms (FCFS, SSTF, SCAN, LOOK)", plannedLectures: 3, completedLectures: 0, targetDate: "2026-11-15", status: "Pending" }
        ]
      }
    ],
    "Practical/Lab": [
      {
        unitId: "OSP-U1",
        unitNumber: 1,
        unitTitle: "Linux Environment & Process Control Lab",
        topics: [
          { id: "OSP-1.1", order: 1, name: "Linux Shell Scripting & Basic OS Command Utilities", plannedLectures: 2, completedLectures: 2, targetDate: "2026-08-15", status: "Completed" },
          { id: "OSP-1.2", order: 2, name: "Process Control Calls (fork, exec, wait, exit) in C", plannedLectures: 2, completedLectures: 2, targetDate: "2026-08-29", status: "Completed" }
        ]
      },
      {
        unitId: "OSP-U2",
        unitNumber: 2,
        unitTitle: "CPU Scheduling & Synchronization Simulation",
        topics: [
          { id: "OSP-2.1", order: 3, name: "Simulation of CPU Scheduling Algorithms (FCFS, SJF, RR)", plannedLectures: 3, completedLectures: 3, targetDate: "2026-09-15", status: "Completed" },
          { id: "OSP-2.2", order: 4, name: "Producer-Consumer Problem using POSIX Semaphores", plannedLectures: 3, completedLectures: 1, targetDate: "2026-09-30", status: "Ongoing" }
        ]
      },
      {
        unitId: "OSP-U3",
        unitNumber: 3,
        unitTitle: "Deadlocks & Memory Management Lab",
        topics: [
          { id: "OSP-3.1", order: 5, name: "Banker's Algorithm for Deadlock Avoidance in C", plannedLectures: 2, completedLectures: 0, targetDate: "2026-10-25", status: "Pending" },
          { id: "OSP-3.2", order: 6, name: "Page Replacement Algorithms Simulation (FIFO, LRU, Optimal)", plannedLectures: 2, completedLectures: 0, targetDate: "2026-11-10", status: "Pending" }
        ]
      }
    ]
  },
  "Computer Networks": {
    "Theory": [
      {
        unitId: "CNT-U1",
        unitNumber: 1,
        unitTitle: "Introduction to Physical & Data Link Layer",
        topics: [
          { id: "CNT-1.1", order: 1, name: "Network Topologies, OSI Reference Model & TCP/IP Protocol Stack", plannedLectures: 3, completedLectures: 3, targetDate: "2026-08-14", status: "Completed" },
          { id: "CNT-1.2", order: 2, name: "Transmission Media, Framing & Error Detection (CRC, Checksum)", plannedLectures: 3, completedLectures: 3, targetDate: "2026-08-22", status: "Completed" }
        ]
      },
      {
        unitId: "CNT-U2",
        unitNumber: 2,
        unitTitle: "Medium Access Control (MAC) Sublayer",
        topics: [
          { id: "CNT-2.1", order: 3, name: "ALOHA Protocols, CSMA/CD, CSMA/CA & Collision Avoidance", plannedLectures: 4, completedLectures: 4, targetDate: "2026-09-08", status: "Completed" },
          { id: "CNT-2.2", order: 4, name: "Ethernet Standards (IEEE 802.3) & Wireless LAN (IEEE 802.11)", plannedLectures: 4, completedLectures: 4, targetDate: "2026-09-22", status: "Completed" }
        ]
      },
      {
        unitId: "CNT-U3",
        unitNumber: 3,
        unitTitle: "Transport Layer Protocols",
        topics: [
          { id: "CNT-3.1", order: 5, name: "Transport Service, Elements of Transport Protocols & Addressing", plannedLectures: 4, completedLectures: 4, targetDate: "2026-10-06", status: "Completed" },
          { id: "CNT-3.2", order: 6, name: "TCP Connection Management, Flow Control & Congestion Control", plannedLectures: 4, completedLectures: 0, targetDate: "2026-10-24", status: "Ongoing" }
        ]
      },
      {
        unitId: "CNT-U4",
        unitNumber: 4,
        unitTitle: "Network Layer & Routing Protocols",
        topics: [
          { id: "CNT-4.1", order: 7, name: "IPv4 Addressing, Subnetting, CIDR & NAT", plannedLectures: 4, completedLectures: 0, targetDate: "2026-11-04", status: "Pending" },
          { id: "CNT-4.2", order: 8, name: "Routing Algorithms: Distance Vector & Link State Routing (OSPF, RIP)", plannedLectures: 4, completedLectures: 0, targetDate: "2026-11-14", status: "Pending" }
        ]
      },
      {
        unitId: "CNT-U5",
        unitNumber: 5,
        unitTitle: "Application Layer & Network Security",
        topics: [
          { id: "CNT-5.1", order: 9, name: "DNS, HTTP, HTTPS, FTP, SMTP & Email Architecture", plannedLectures: 3, completedLectures: 0, targetDate: "2026-11-22", status: "Pending" },
          { id: "CNT-5.2", order: 10, name: "Cryptography Basics, Digital Signatures & Firewalls", plannedLectures: 3, completedLectures: 0, targetDate: "2026-11-30", status: "Pending" }
        ]
      }
    ],
    "Practical/Lab": [
      {
        unitId: "CNP-U1",
        unitNumber: 1,
        unitTitle: "Packet Analysis & Data Link Simulation",
        topics: [
          { id: "CNP-1.1", order: 1, name: "Packet Sniffing & WireShark Protocol Analysis", plannedLectures: 2, completedLectures: 2, targetDate: "2026-08-20", status: "Completed" },
          { id: "CNP-1.2", order: 2, name: "Implementation of Error Detection Codes (CRC-32) in C/Python", plannedLectures: 3, completedLectures: 3, targetDate: "2026-09-05", status: "Completed" }
        ]
      },
      {
        unitId: "CNP-U2",
        unitNumber: 2,
        unitTitle: "Socket Programming & Topology Lab",
        topics: [
          { id: "CNP-2.1", order: 3, name: "Client-Server Socket Programming using TCP & UDP", plannedLectures: 3, completedLectures: 2, targetDate: "2026-09-28", status: "Ongoing" },
          { id: "CNP-2.2", order: 4, name: "Network Configuration and Subnetting on Cisco Packet Tracer", plannedLectures: 3, completedLectures: 0, targetDate: "2026-10-26", status: "Pending" }
        ]
      }
    ]
  }
};

// Generic fallback template for any other course (Theory and Practical/Lab ONLY)
function generateGenericSyllabus(subjectName) {
  return {
    "Theory": [
      {
        unitId: "GT-U1",
        unitNumber: 1,
        unitTitle: `Foundations of ${subjectName}`,
        topics: [
          { id: "GT-1.1", order: 1, name: "Core Principles & Architectural Foundations", plannedLectures: 3, completedLectures: 3, targetDate: "2026-08-20", status: "Completed" },
          { id: "GT-1.2", order: 2, name: "Theoretical Analysis & System Methodology", plannedLectures: 3, completedLectures: 3, targetDate: "2026-08-30", status: "Completed" }
        ]
      },
      {
        unitId: "GT-U2",
        unitNumber: 2,
        unitTitle: "Core Algorithms & Implementation",
        topics: [
          { id: "GT-2.1", order: 3, name: "Design Patterns & Implementation Algorithms", plannedLectures: 4, completedLectures: 4, targetDate: "2026-09-18", status: "Completed" },
          { id: "GT-2.2", order: 4, name: "Verification, Metrics & System Optimization", plannedLectures: 4, completedLectures: 2, targetDate: "2026-10-05", status: "Ongoing" }
        ]
      },
      {
        unitId: "GT-U3",
        unitNumber: 3,
        unitTitle: "Advanced Applications & Industry Standards",
        topics: [
          { id: "GT-3.1", order: 5, name: "Industry Standard Practices & Tools", plannedLectures: 4, completedLectures: 0, targetDate: "2026-10-28", status: "Pending" },
          { id: "GT-3.2", order: 6, name: "Emerging Trends & Capstone Project", plannedLectures: 4, completedLectures: 0, targetDate: "2026-11-15", status: "Pending" }
        ]
      }
    ],
    "Practical/Lab": [
      {
        unitId: "GP-U1",
        unitNumber: 1,
        unitTitle: `${subjectName} Hands-On Lab Work`,
        topics: [
          { id: "GP-1.1", order: 1, name: "Lab Tooling Setup & Baseline Experiments", plannedLectures: 3, completedLectures: 3, targetDate: "2026-08-25", status: "Completed" },
          { id: "GP-1.2", order: 2, name: "Benchmark Execution & Metric Analysis", plannedLectures: 3, completedLectures: 1, targetDate: "2026-09-25", status: "Ongoing" },
          { id: "GP-1.3", order: 3, name: "Comprehensive Practical System Project", plannedLectures: 4, completedLectures: 0, targetDate: "2026-10-30", status: "Pending" }
        ]
      }
    ]
  };
}

// Generate unique key ensuring total division & subject isolation
function getSyllabusCourseKey(subject, classDiv) {
  return `${subject.trim()}___${classDiv.trim()}`;
}

// Get assigned courses & divisions for a specific faculty from MASTER_TIMETABLE (Theory & Practical ONLY)
function getAssignedCoursesForFaculty(facultyId) {
  const allowedTypes = ["Theory", "Practical/Lab", "Lab Practical"];
  const lectures = MASTER_TIMETABLE.filter(l => l.facultyId === facultyId && allowedTypes.includes(l.type));
  const courseMap = new Map();

  lectures.forEach(l => {
    const key = getSyllabusCourseKey(l.subject, l.classDiv);
    if (!courseMap.has(key)) {
      let code = "CS-301";
      if (l.subject.toLowerCase().includes("networks")) code = "CS-204";
      else if (l.subject.toLowerCase().includes("testing")) code = "CS-305";
      else if (l.subject.toLowerCase().includes("discrete")) code = "CS-201";
      else if (l.subject.toLowerCase().includes("database")) code = "CS-302";
      else if (l.subject.toLowerCase().includes("cloud")) code = "CS-401";
      else if (l.subject.toLowerCase().includes("structures")) code = "CS-202";

      courseMap.set(key, {
        code: code,
        subject: l.subject,
        classDiv: l.classDiv,
        key: key
      });
    }
  });

  return Array.from(courseMap.values());
}

// Get or seed syllabus data for a specific subject, division, and optional lecture type
function getSyllabusProgress(courseKey, lectureType) {
  try {
    const rawAll = localStorage.getItem(SYLLABUS_STORAGE_KEY);
    const store = rawAll ? JSON.parse(rawAll) : {};

    if (!store[courseKey] || Array.isArray(store[courseKey]) || !store[courseKey].Theory) {
      // Determine template based on authentic subject records
      const [subject] = courseKey.split("___");
      let template = DEFAULT_SYLLABUS_TEMPLATES[subject];
      if (!template && (subject.includes("Operating System") || subject.includes("OS"))) {
        template = DEFAULT_SYLLABUS_TEMPLATES["Operating Systems"];
      }
      if (!template) {
        // Genuine empty state: do not fabricate generic topics or percentages
        template = { Theory: [], "Practical/Lab": [] };
      }

      // Deep clone to guarantee complete division isolation
      const cloned = JSON.parse(JSON.stringify(template));
      store[courseKey] = cloned;
      localStorage.setItem(SYLLABUS_STORAGE_KEY, JSON.stringify(store));
    }

    if (lectureType === "Theory") {
      return store[courseKey].Theory || [];
    } else if (lectureType === "Practical/Lab") {
      return store[courseKey]["Practical/Lab"] || [];
    }
    return store[courseKey];
  } catch (e) {
    console.error(e);
    return lectureType ? [] : { Theory: [], "Practical/Lab": [] };
  }
}

// Save syllabus data for a specific subject, division, and lecture type
function saveSyllabusProgress(courseKey, lectureType, units) {
  try {
    const rawAll = localStorage.getItem(SYLLABUS_STORAGE_KEY);
    const store = rawAll ? JSON.parse(rawAll) : {};

    if (!store[courseKey] || Array.isArray(store[courseKey])) {
      store[courseKey] = { Theory: [], "Practical/Lab": [] };
    }

    if (lectureType === "Theory" || lectureType === "Practical/Lab") {
      store[courseKey][lectureType] = units;
    } else {
      store[courseKey] = units;
    }

    localStorage.setItem(SYLLABUS_STORAGE_KEY, JSON.stringify(store));
    return true;
  } catch (e) {
    console.error(e);
    return false;
  }
}

// Get recorded lecture activity logs for a subject and division
function getLectureActivityLogs(courseKey) {
  try {
    const rawAll = localStorage.getItem(LECTURE_LOG_STORAGE_KEY);
    const store = rawAll ? JSON.parse(rawAll) : {};
    return store[courseKey] || [];
  } catch (e) {
    return [];
  }
}

// Save lecture activity log with duplicate prevention
function recordLectureActivity(courseKey, logEntry) {
  try {
    const rawAll = localStorage.getItem(LECTURE_LOG_STORAGE_KEY);
    const store = rawAll ? JSON.parse(rawAll) : {};
    const logs = store[courseKey] || [];

    // Duplicate check: prevent recording the exact same slot on the same date twice
    const isDuplicate = logs.some(
      l => l.date === logEntry.date && l.slotTime === logEntry.slotTime
    );

    if (isDuplicate) {
      return {
        success: false,
        error: `Duplicate Record: A lecture activity log for ${logEntry.date} (${logEntry.slotTime}) already exists.`
      };
    }

    const effectiveType = (logEntry.lectureType === "Practical/Lab" || logEntry.lectureType === "Lab Practical") 
      ? "Practical/Lab" 
      : "Theory";

    const newLog = {
      id: `LOG-${Date.now()}`,
      date: logEntry.date,
      slotTime: logEntry.slotTime,
      slotDay: logEntry.slotDay,
      room: logEntry.room,
      lectureType: effectiveType,
      topicId: logEntry.topicId,
      topicName: logEntry.topicName,
      status: logEntry.status, // "Completed" | "Cancelled" | "Not Conducted"
      remarks: logEntry.remarks || "",
      recordedAt: new Date().toISOString()
    };

    logs.unshift(newLog);
    store[courseKey] = logs;
    localStorage.setItem(LECTURE_LOG_STORAGE_KEY, JSON.stringify(store));

    // ONLY COMPLETED lectures increment completedLectures count in syllabus!
    // Cancelled and Not Conducted NEVER count as completed!
    if (logEntry.status === "Completed") {
      const units = getSyllabusProgress(courseKey, effectiveType);
      let foundTopic = null;
      units.forEach(u => {
        const t = u.topics.find(top => top.id === logEntry.topicId);
        if (t) foundTopic = t;
      });

      if (foundTopic) {
        foundTopic.completedLectures = (foundTopic.completedLectures || 0) + 1;
        if (foundTopic.completedLectures >= foundTopic.plannedLectures) {
          foundTopic.status = "Completed";
        } else {
          foundTopic.status = "Ongoing";
        }
        saveSyllabusProgress(courseKey, effectiveType, units);
      }
    }

    return { success: true, log: newLog };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

// Delete a recorded lecture activity log
function deleteLectureActivityLog(courseKey, logId) {
  try {
    const rawAll = localStorage.getItem(LECTURE_LOG_STORAGE_KEY);
    const store = rawAll ? JSON.parse(rawAll) : {};
    const logs = store[courseKey] || [];

    const targetIdx = logs.findIndex(l => l.id === logId);
    if (targetIdx === -1) return { success: false, error: "Record not found." };

    const target = logs[targetIdx];

    // Revert completed lecture count on syllabus if it was completed
    if (target.status === "Completed") {
      const effectiveType = target.lectureType === "Practical/Lab" ? "Practical/Lab" : "Theory";
      const units = getSyllabusProgress(courseKey, effectiveType);
      let foundTopic = null;
      units.forEach(u => {
        const t = u.topics.find(top => top.id === target.topicId);
        if (t) foundTopic = t;
      });

      if (foundTopic && foundTopic.completedLectures > 0) {
        foundTopic.completedLectures -= 1;
        if (foundTopic.completedLectures === 0) {
          foundTopic.status = "Pending";
        } else {
          foundTopic.status = "Ongoing";
        }
        saveSyllabusProgress(courseKey, effectiveType, units);
      }
    }

    logs.splice(targetIdx, 1);
    store[courseKey] = logs;
    localStorage.setItem(LECTURE_LOG_STORAGE_KEY, JSON.stringify(store));
    return { success: true };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

// Reorder syllabus topics up or down in teaching sequence for a lecture type
function reorderSyllabusTopic(courseKey, lectureType, topicId, direction) {
  const effectiveType = lectureType === "Practical/Lab" ? "Practical/Lab" : "Theory";
  const units = getSyllabusProgress(courseKey, effectiveType);

  for (let u of units) {
    const idx = u.topics.findIndex(t => t.id === topicId);
    if (idx !== -1) {
      if (direction === "up" && idx > 0) {
        const temp = u.topics[idx - 1];
        u.topics[idx - 1] = u.topics[idx];
        u.topics[idx] = temp;
      } else if (direction === "down" && idx < u.topics.length - 1) {
        const temp = u.topics[idx + 1];
        u.topics[idx + 1] = u.topics[idx];
        u.topics[idx] = temp;
      }
      let currentOrder = 1;
      units.forEach(unit => {
        unit.topics.forEach(t => {
          t.order = currentOrder++;
        });
      });
      saveSyllabusProgress(courseKey, effectiveType, units);
      return true;
    }
  }
  return false;
}

// Update planned lecture count & target completion date for a topic
function updateTopicPlan(courseKey, lectureType, topicId, updates) {
  const effectiveType = lectureType === "Practical/Lab" ? "Practical/Lab" : "Theory";
  const units = getSyllabusProgress(courseKey, effectiveType);
  let updated = false;

  units.forEach(u => {
    const t = u.topics.find(top => top.id === topicId);
    if (t) {
      if (updates.plannedLectures !== undefined) t.plannedLectures = Math.max(1, parseInt(updates.plannedLectures, 10));
      if (updates.targetDate !== undefined) t.targetDate = updates.targetDate;
      if (updates.name !== undefined) t.name = updates.name.trim();

      if (t.completedLectures >= t.plannedLectures) {
        t.status = "Completed";
      } else if (t.completedLectures > 0) {
        t.status = "Ongoing";
      } else {
        t.status = "Pending";
      }
      updated = true;
    }
  });

  if (updated) {
    saveSyllabusProgress(courseKey, effectiveType, units);
    return true;
  }
  return false;
}

// Reschedule a pending topic to a new target date
function reschedulePendingTopic(courseKey, lectureType, topicId, newDate) {
  return updateTopicPlan(courseKey, lectureType, topicId, { targetDate: newDate });
}

// Calculate comprehensive syllabus progress metrics (Division-isolated, Theory vs Practical, Delay alerts)
function calculateSyllabusMetrics(courseKey) {
  const todayStr = new Date().toISOString().split("T")[0];
  const theoryUnits = getSyllabusProgress(courseKey, "Theory");
  const practicalUnits = getSyllabusProgress(courseKey, "Practical/Lab");
  const logs = getLectureActivityLogs(courseKey);

  function computeUnitMetrics(units, typeLabel) {
    let planned = 0;
    let completed = 0;
    let completedTopics = 0;
    let ongoingTopics = 0;
    let pendingTopics = 0;
    const delayed = [];

    units.forEach(u => {
      let uDone = 0;
      u.topics.forEach(t => {
        planned += (t.plannedLectures || 0);
        completed += (t.completedLectures || 0);
        const isDel = t.targetDate < todayStr && t.status !== "Completed";
        if (isDel) {
          delayed.push({
            topicId: t.id,
            topicName: t.name,
            unitTitle: u.unitTitle,
            targetDate: t.targetDate,
            type: typeLabel,
            plannedLectures: t.plannedLectures,
            completedLectures: t.completedLectures
          });
        }
        if (t.status === "Completed") {
          completedTopics++;
          uDone++;
        } else if (t.status === "Ongoing") {
          ongoingTopics++;
        } else {
          pendingTopics++;
        }
      });
      u.isUnitCompleted = uDone === u.topics.length && u.topics.length > 0;
    });

    const remaining = Math.max(0, planned - completed);
    const pct = planned > 0 ? Math.min(100, Math.round((completed / planned) * 100)) : 0;

    return {
      planned,
      completed,
      remaining,
      percentage: pct,
      completedTopics,
      ongoingTopics,
      pendingTopics,
      totalTopics: completedTopics + ongoingTopics + pendingTopics,
      delayed,
      unitsCount: units.length,
      completedUnitsCount: units.filter(u => u.isUnitCompleted).length
    };
  }

  const theory = computeUnitMetrics(theoryUnits, "Theory");
  const practical = computeUnitMetrics(practicalUnits, "Practical/Lab");

  const totalPlannedLectures = theory.planned + practical.planned;
  const totalCompletedLectures = theory.completed + practical.completed;
  const remainingLectures = Math.max(0, totalPlannedLectures - totalCompletedLectures);
  const overallPercentage = totalPlannedLectures > 0 
    ? Math.min(100, Math.round((totalCompletedLectures / totalPlannedLectures) * 100)) 
    : 0;

  const conductedCount = logs.filter(l => l.status === "Completed").length;
  const cancelledCount = logs.filter(l => l.status === "Cancelled").length;
  const notConductedCount = logs.filter(l => l.status === "Not Conducted").length;

  const allDelayed = [...theory.delayed, ...practical.delayed];

  // Division-wise comparisons for Power BI visualization (e.g. AD-1 vs AD-3 for the same subject)
  const [subject, currentDiv] = courseKey.split("___");
  const divisionComparisons = [];
  try {
    const rawAll = localStorage.getItem(SYLLABUS_STORAGE_KEY);
    const store = rawAll ? JSON.parse(rawAll) : {};
    Object.keys(store).forEach(k => {
      const [sName, dName] = k.split("___");
      if (sName === subject) {
        const dTheory = store[k].Theory || [];
        const dPract = store[k]["Practical/Lab"] || [];
        let dPlan = 0, dComp = 0;
        [...dTheory, ...dPract].forEach(u => {
          (u.topics || []).forEach(t => {
            dPlan += (t.plannedLectures || 0);
            dComp += (t.completedLectures || 0);
          });
        });
        const dPct = dPlan > 0 ? Math.min(100, Math.round((dComp / dPlan) * 100)) : 0;
        divisionComparisons.push({
          division: dName,
          percentage: dPct,
          isCurrent: dName === currentDiv
        });
      }
    });
  } catch (e) {}

  return {
    totalPlannedLectures,
    totalCompletedLectures,
    remainingLectures,
    overallPercentage,
    conductedCount,
    cancelledCount,
    notConductedCount,
    delayedTopics: allDelayed,
    totalTopicsCount: theory.totalTopics + practical.totalTopics,
    completedTopicsCount: theory.completedTopics + practical.completedTopics,
    ongoingTopicsCount: theory.ongoingTopics + practical.ongoingTopics,
    pendingTopicsCount: theory.pendingTopics + practical.pendingTopics,
    theory,
    practical,
    divisionComparisons
  };
}

// Generate Power BI CSV Dataset for syllabus tracking
function generateSyllabusPowerBICSV() {
  const headers = [
    "Faculty_ID",
    "Faculty_Name",
    "Subject",
    "Class_Division",
    "Lecture_Type",
    "Unit_Number",
    "Unit_Title",
    "Topic_ID",
    "Teaching_Order",
    "Topic_Name",
    "Planned_Lectures",
    "Completed_Lectures",
    "Target_Completion_Date",
    "Topic_Status",
    "Is_Delayed"
  ];

  const todayStr = new Date().toISOString().split("T")[0];
  const rows = [];

  MASTER_FACULTY_LIST.forEach(f => {
    const assigned = getAssignedCoursesForFaculty(f.id);
    assigned.forEach(c => {
      const types = ["Theory", "Practical/Lab"];
      types.forEach(lType => {
        const units = getSyllabusProgress(c.key, lType);
        units.forEach(u => {
          u.topics.forEach(t => {
            const isDelayed = t.targetDate < todayStr && t.status !== "Completed" ? "Yes" : "No";
            rows.push([
              `"${f.id}"`,
              `"${f.name}"`,
              `"${c.subject}"`,
              `"${c.classDiv}"`,
              `"${lType}"`,
              u.unitNumber,
              `"${u.unitTitle}"`,
              `"${t.id}"`,
              t.order,
              `"${t.name}"`,
              t.plannedLectures,
              t.completedLectures,
              `"${t.targetDate}"`,
              `"${t.status}"`,
              `"${isDelayed}"`
            ]);
          });
        });
      });
    });
  });

  return [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
}

function downloadSyllabusPowerBICSV() {
  const csvContent = generateSyllabusPowerBICSV();
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", `edunova_syllabus_tracking_powerbi_${new Date().toISOString().split("T")[0]}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Generate Power BI CSV Dataset for timetable-linked lecture activity logs
function generateLectureActivityPowerBICSV() {
  const headers = [
    "Faculty_ID",
    "Faculty_Name",
    "Subject",
    "Class_Division",
    "Lecture_Type",
    "Date",
    "Day_Of_Week",
    "Timetable_Slot_Time",
    "Room",
    "Topic_ID",
    "Topic_Name",
    "Lecture_Status",
    "Remarks",
    "Recorded_Timestamp"
  ];

  const rows = [];
  try {
    const rawAll = localStorage.getItem(LECTURE_LOG_STORAGE_KEY);
    const store = rawAll ? JSON.parse(rawAll) : {};

    MASTER_FACULTY_LIST.forEach(f => {
      const assigned = getAssignedCoursesForFaculty(f.id);
      assigned.forEach(c => {
        const logs = store[c.key] || [];
        logs.forEach(log => {
          rows.push([
            `"${f.id}"`,
            `"${f.name}"`,
            `"${c.subject}"`,
            `"${c.classDiv}"`,
            `"${log.lectureType || 'Theory'}"`,
            `"${log.date}"`,
            `"${log.slotDay || ''}"`,
            `"${log.slotTime || ''}"`,
            `"${log.room || ''}"`,
            `"${log.topicId || ''}"`,
            `"${(log.topicName || '').replace(/"/g, '""')}"`,
            `"${log.status}"`,
            `"${(log.remarks || '').replace(/"/g, '""')}"`,
            `"${log.recordedAt || ''}"`
          ]);
        });
      });
    });
  } catch (e) {
    console.error(e);
  }

  return [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
}

function downloadLectureActivityPowerBICSV() {
  const csvContent = generateLectureActivityPowerBICSV();
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", `edunova_lecture_activity_powerbi_${new Date().toISOString().split("T")[0]}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Complete JSON export matching timetable and syllabus schema for Power BI / Power Query
function downloadSyllabusJSON() {
  const payload = {
    exportedAt: new Date().toISOString(),
    system: "EduNova Smart Faculty Timetable & Syllabus Tracking",
    facultyCourses: []
  };

  try {
    const rawSyllabus = localStorage.getItem(SYLLABUS_STORAGE_KEY);
    const syllabusStore = rawSyllabus ? JSON.parse(rawSyllabus) : {};
    const rawLogs = localStorage.getItem(LECTURE_LOG_STORAGE_KEY);
    const logStore = rawLogs ? JSON.parse(rawLogs) : {};

    MASTER_FACULTY_LIST.forEach(f => {
      const assigned = getAssignedCoursesForFaculty(f.id);
      assigned.forEach(c => {
        payload.facultyCourses.push({
          facultyId: f.id,
          facultyName: f.name,
          department: f.dept,
          courseCode: c.code,
          subject: c.subject,
          classDiv: c.classDiv,
          courseKey: c.key,
          syllabus: syllabusStore[c.key] || getSyllabusProgress(c.key),
          lectureLogs: logStore[c.key] || []
        });
      });
    });
  } catch (e) {
    console.error(e);
  }

  const jsonStr = JSON.stringify(payload, null, 2);
  const blob = new Blob([jsonStr], { type: "application/json;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", `edunova_syllabus_dataset_powerbi_${new Date().toISOString().split("T")[0]}.json`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}




// ----- Synthetic Faculty & Conflict Timetable Data -----

// Add two synthetic faculty members for testing
const SYNTHETIC_FACULTY = [];

// Extend master faculty list with synthetic entries (if not already present)
SYNTHETIC_FACULTY.forEach(f => {
  if (!MASTER_FACULTY_LIST.find(mf => mf.id === f.id)) {
    MASTER_FACULTY_LIST.push({
      id: f.id,
      name: f.name,
      dept: f.dept,
      designation: f.designation,
      classes: f.classes,
      email: f.email
    });
  }
});

// Synthetic timetable designed to trigger each conflict type (12–15 entries)
const SYNTHETIC_CONFLICT_TIMETABLE = [];

// ----- Conflict Detection Engine -----
/**
 * Detect overlapping entries in a given timetable array.
 * Returns an array of conflict objects with detailed description.
 */
function detectTimetableConflicts(timetable = MASTER_TIMETABLE) {
  const conflicts = [];
  const entries = timetable.slice(); // shallow copy

  // Helper to determine time overlap for same day
  const overlap = (a, b) => !(a.endTime <= b.startTime || a.startTime >= b.endTime);

  for (let i = 0; i < entries.length; i++) {
    for (let j = i + 1; j < entries.length; j++) {
      const a = entries[i];
      const b = entries[j];
      if (a.day !== b.day) continue; // only same day matters

      if (overlap(a, b)) {
        // Faculty overlap
        if (a.facultyId === b.facultyId) {
          conflicts.push({
            conflictType: 'faculty-overlap',
            severity: 'critical',
            entryA: a,
            entryB: b,
            description: `${a.facultyName} is double‑booked on ${a.day} (${a.displayTime} vs ${b.displayTime}).`
          });
        }
        // Room overlap
        if (a.room === b.room) {
          conflicts.push({
            conflictType: 'room-overlap',
            severity: 'critical',
            entryA: a,
            entryB: b,
            description: `Room ${a.room} has two lectures on ${a.day} (${a.displayTime} vs ${b.displayTime}).`
          });
        }
        // Division overlap
        if (a.classDiv === b.classDiv) {
          conflicts.push({
            conflictType: 'division-overlap',
            severity: 'warning',
            entryA: a,
            entryB: b,
            description: `Division ${a.classDiv} is assigned two lectures on ${a.day} (${a.displayTime} vs ${b.displayTime}).`
          });
        }
        // Lab‑faculty conflict: a lab entry where the same faculty also has a theory entry at overlapping time
        if (a.type.toLowerCase().includes('lab') && b.type.toLowerCase() === 'theory' && a.facultyId === b.facultyId) {
          conflicts.push({
            conflictType: 'lab-faculty-conflict',
            severity: 'warning',
            entryA: a,
            entryB: b,
            description: `${a.facultyName} has a lab and theory lecture overlapping on ${a.day} (${a.displayTime} vs ${b.displayTime}).`
          });
        }
        if (b.type.toLowerCase().includes('lab') && a.type.toLowerCase() === 'theory' && a.facultyId === b.facultyId) {
          conflicts.push({
            conflictType: 'lab-faculty-conflict',
            severity: 'warning',
            entryA: b,
            entryB: a,
            description: `${b.facultyName} has a lab and theory lecture overlapping on ${b.day} (${b.displayTime} vs ${a.displayTime}).`
          });
        }
      }
    }
  }
  return conflicts;
}

/**
 * Find replacement candidates for a conflicted entry.
 * Returns an array sorted with recommended candidates first.
 */
function findReplacementCandidates(conflictEntry, timetable = MASTER_TIMETABLE) {
  const allFaculty = MASTER_FACULTY_LIST.concat(SYNTHETIC_FACULTY);
  const originalFaculty = allFaculty.find(f => f.id === conflictEntry.facultyId);
  if (!originalFaculty) return [];

  const candidates = allFaculty.filter(f => {
    // Same department, not the original faculty
    if (f.dept !== originalFaculty.dept || f.id === originalFaculty.id) return false;

    // Check no overlapping entry for this faculty on the same day & time slot
    const overlap = timetable.some(e => {
      return e.facultyId === f.id &&
        e.day === conflictEntry.day &&
        !(e.endTime <= conflictEntry.startTime || e.startTime >= conflictEntry.endTime);
    });
    if (overlap) return false;

    // Additionally check duty assignments (if any) – using existing helper
    const duties = getFacultyDutyAssignments ? getFacultyDutyAssignments(f.id) : [];
    const dutyOverlap = duties.some(d => {
      return d.day === conflictEntry.day &&
        !(d.endTime <= conflictEntry.startTime || d.startTime >= conflictEntry.endTime);
    });
    if (dutyOverlap) return false;

    return true;
  }).map(f => {
    // Determine if the candidate teaches the same subject (heuristic: class list contains same subject prefix)
    const teachesSameSubject = (f.classes || []).some(cls => cls.includes(conflictEntry.subject.split(' ')[0]));
    return {
      facultyId: f.id,
      facultyName: f.name,
      dept: f.dept,
      designation: f.designation,
      isRecommended: teachesSameSubject,
      recommendReason: teachesSameSubject ? 'Same subject expertise' : 'Available faculty',
      availableSlot: `${conflictEntry.day} ${conflictEntry.displayTime}`
    };
  });

  // Sort recommended first
  candidates.sort((a, b) => (b.isRecommended - a.isRecommended));
  return candidates;
}

/**
 * Validate a replacement before confirming.
 * Re‑checks availability, room, and division constraints.
 */
function validateReplacementBeforeConfirm(originalEntry, replacementFacultyId, timetable = MASTER_TIMETABLE) {
  const replacement = (MASTER_FACULTY_LIST.concat(SYNTHETIC_FACULTY)).find(f => f.id === replacementFacultyId);
  if (!replacement) return { valid: false, reason: 'Replacement faculty not found.' };

  // 1️⃣ Faculty still free?
  const facultyBusy = timetable.some(e => {
    return e.facultyId === replacementFacultyId &&
      e.day === originalEntry.day &&
      !(e.endTime <= originalEntry.startTime || e.startTime >= originalEntry.endTime);
  });
  if (facultyBusy) return { valid: false, reason: 'Replacement faculty has another lecture at this time.' };

  // 2️⃣ Room still free?
  const roomBusy = timetable.some(e => {
    return e.room === originalEntry.room &&
      e.day === originalEntry.day &&
      !(e.endTime <= originalEntry.startTime || e.startTime >= originalEntry.endTime);
  });
  if (roomBusy) return { valid: false, reason: 'Room is double‑booked for the selected slot.' };

  // 3️⃣ Division still free?
  const divisionBusy = timetable.some(e => {
    return e.classDiv === originalEntry.classDiv &&
      e.day === originalEntry.day &&
      !(e.endTime <= originalEntry.startTime || e.startTime >= originalEntry.endTime);
  });
  if (divisionBusy) return { valid: false, reason: 'Division already has a lecture at this time.' };

  return { valid: true };
}

// ----- LocalStorage Helpers for Confirmed Replacements -----
const CONFLICT_REPLACEMENT_STORAGE_KEY = 'edunova_conflict_replacements_v1';
function getConfirmedConflictReplacements() {
  const raw = localStorage.getItem(CONFLICT_REPLACEMENT_STORAGE_KEY);
  return raw ? JSON.parse(raw) : [];
}
function confirmConflictReplacement(originalEntry, replacementFaculty, notes = '') {
  const records = getConfirmedConflictReplacements();
  records.push({
    originalFacultyId: originalEntry.facultyId,
    originalFacultyName: originalEntry.facultyName,
    subject: originalEntry.subject,
    day: originalEntry.day,
    time: originalEntry.displayTime,
    room: originalEntry.room,
    replacementFacultyId: replacementFaculty.facultyId,
    replacementFacultyName: replacementFaculty.facultyName,
    conflictType: originalEntry.conflictType || 'unspecified',
    notes,
    confirmedAt: new Date().toISOString()
  });
  localStorage.setItem(CONFLICT_REPLACEMENT_STORAGE_KEY, JSON.stringify(records));
  return { success: true };
}

// Expose functions for UI scripts (attach to window)
if (typeof window !== 'undefined') {
  window.edunovaConflictEngine = {
    detectTimetableConflicts,
    findReplacementCandidates,
    validateReplacementBeforeConfirm,
    getConfirmedConflictReplacements,
    confirmConflictReplacement,
    syntheticTimetable: SYNTHETIC_CONFLICT_TIMETABLE
  };
}
// =====================================================
// Additional Sample Data: Ensure 2 Theory Lectures + 1 Lab per Division for each Faculty
// =====================================================
// This block adds generic placeholder entries for any missing slots.
// Times are chosen to avoid clashes with existing schedule.
// NOTE: Adjust IDs and times as needed for real deployment.

const additionalSampleData = [];

// Merge additional data into master timetable
MASTER_TIMETABLE.push(...additionalSampleData);


// =============================================================================
// LIVE BACKEND API SYNCHRONIZATION
// =============================================================================
async function syncTimetableFromAPI() {
  const token = localStorage.getItem('edunova_token');
  if (!token) return;

  try {
    // 1. Verify user identity
    const meRes = await fetch('/api/auth/me', {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (meRes.status === 401) {
      console.warn("Session expired. Redirecting to login...");
      localStorage.removeItem('edunova_token');
      localStorage.removeItem('edunova_auth_user');
      window.location.href = 'index.html';
      return;
    }

    if (meRes.ok) {
      const meData = await meRes.json();
      localStorage.setItem('edunova_auth_user', JSON.stringify(meData));
      localStorage.setItem('edunova_active_faculty_id', meData.faculty_id || meData.id);
    }

    // 2. Fetch live faculty directory
    const facRes = await fetch('/api/faculty', {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (facRes.ok) {
      const facData = await facRes.json();
      if (Array.isArray(facData) && facData.length > 0) {
        MASTER_FACULTY_LIST.length = 0;
        facData.forEach(f => {
          // Exclude pure administrative accounts (e.g. ADM-101) from ordinary teaching faculty roster
          if (f.faculty_id === 'ADM-101' || f.id === 1) return;
          MASTER_FACULTY_LIST.push({
            id: f.faculty_id || `FAC-${f.id}`,
            dbId: f.id,
            name: f.name,
            dept: f.department || "Artificial Intelligence and Data Science (AI&DS)",
            designation: f.role === 'admin' ? "HOD / Administrator" : (f.name.includes("Dr.") ? "Professor" : "Assistant Professor"),
            classes: ["SY AD1", "SY AD2", "SY AD3", "TY AD1", "TY AD2", "BE AD1", "BE AD2"],
            email: f.email,
            maxHours: f.max_hours || 16,
            role: f.role,
            active: f.active !== false && f.active !== 0
          });
        });
      }
    }

    // 3. Fetch live timetable entries from database
    const ttRes = await fetch('/api/timetable', {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (ttRes.ok) {
      const ttData = await ttRes.json();
      if (Array.isArray(ttData) && ttData.length > 0) {
        MASTER_TIMETABLE.length = 0;
        ttData.forEach(item => {
          MASTER_TIMETABLE.push({
            id: `SCH-${item.id}`,
            dbId: item.id,
            day: item.day,
            startTime: item.start_time || item.startTime,
            endTime: item.end_time || item.endTime,
            displayTime: item.displayTime || `${item.start_time} - ${item.end_time}`,
            subject: item.subject,
            facultyId: item.facultyId || (item.faculty ? item.faculty.faculty_id : (item.faculty_id ? `FAC-${item.faculty_id}` : null)),
            facultyDbId: item.faculty_id,
            faculty_id: item.faculty_id,
            facultyName: item.facultyName || item.faculty_name || "",
            classDiv: item.display_class || item.classDiv || formatClassWithBatch(item.class_name || item.className || item.classDiv, item.batch, Boolean(item.is_lab)),
            className: item.class_name || item.className || (item.classDiv || "").replace(/\s*\([A-Za-z0-9\s]+\)$/, "").trim(),
            displayClass: item.display_class || item.classDiv || formatClassWithBatch(item.class_name || item.className || item.classDiv, item.batch, Boolean(item.is_lab)),
            room: item.room,
            batch: item.batch,
            batchLetter: item.batch_letter || extractBatchLetter(item.batch),
            type: item.type || (item.is_lab ? "Lab Practical" : "Theory"),
            isLab: Boolean(item.is_lab)
          });
        });
      }
    }

    // 4. Fetch live substitute requests from database
    try {
      const subRes = await fetch('/api/substitutes/requests', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (subRes.ok) {
        const subData = await subRes.json();
        if (Array.isArray(subData)) {
          localStorage.setItem(REPLACEMENT_STORAGE_KEY, JSON.stringify(subData));
        }
      }
    } catch (e) {}

    // Re-render UI components with freshly synced database records
    if (typeof updateFacultyProfileDisplay === 'function') updateFacultyProfileDisplay();
    if (typeof renderFacultyTodayTimetable === 'function') renderFacultyTodayTimetable();
    if (typeof renderFacultyFullTimetable === 'function') renderFacultyFullTimetable();
    if (typeof updateFacultyBadgeCounters === 'function') updateFacultyBadgeCounters();
    if (typeof renderFacultyWorkloadModule === 'function') renderFacultyWorkloadModule();
    if (typeof renderFacultyDirectoryTable === 'function') renderFacultyDirectoryTable();
    if (typeof renderAdminTodayTimetable === 'function') renderAdminTodayTimetable();
    if (typeof renderClassroomsTable === 'function') renderClassroomsTable();
    if (typeof renderLabsTable === 'function') renderLabsTable();
    if (typeof renderAdminReplacementRequests === 'function') renderAdminReplacementRequests();
    if (typeof populateWorkloadFacultyDropdown === 'function') populateWorkloadFacultyDropdown();
    if (typeof renderSelectedFacultyWorkload === 'function') renderSelectedFacultyWorkload();
    if (typeof renderCrossFacultyWorkloadComparison === 'function') renderCrossFacultyWorkloadComparison();
    if (typeof renderRoomsAndLaboratoriesStatus === 'function') renderRoomsAndLaboratoriesStatus();
    if (typeof renderPowerBISectionVisuals === 'function') renderPowerBISectionVisuals();
    if (typeof renderReportsDepartmentOverview === 'function') renderReportsDepartmentOverview();
    if (typeof updateAdminDashboardSummaryCards === 'function') updateAdminDashboardSummaryCards();
  } catch (err) {
    console.warn("Could not sync with live backend; using cached records:", err);
  }
}

// Auto-trigger sync on DOM ready
if (typeof window !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', syncTimetableFromAPI);
  } else {
    syncTimetableFromAPI();
  }
}


// Global Logout Handler
function logoutUser(e) {
  if (e && e.preventDefault) e.preventDefault();
  const token = localStorage.getItem('edunova_token');
  if (token) {
    fetch('/api/auth/logout', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    }).catch(function() {});
  }
  localStorage.removeItem('edunova_token');
  localStorage.removeItem('edunova_auth_user');
  localStorage.removeItem('edunova_active_faculty_id');
  window.location.href = 'index.html';
}
if (typeof window !== 'undefined') {
  window.logoutUser = logoutUser;
}
