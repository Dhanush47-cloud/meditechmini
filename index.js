const functions = require("firebase-functions");
const admin = require("firebase-admin");
admin.initializeApp();

// This function triggers when a new user signs up
exports.createUserProfile = functions.auth.user().onCreate(async (user) => {
  const db = admin.firestore();
  const uid = user.uid;
  const now = admin.firestore.FieldValue.serverTimestamp();

  // Default role = patient (you can later change to doctor/pharmacy via admin)
  const role = "patient";

  // Create a /users record
  await db.collection("users").doc(uid).set({
    uid,
    email: user.email || null,
    role,
    created_at: now
  });

  // Create the /patients record (EHR-style)
  await db.collection("patients").doc(uid).set({
    patient_id: uid,
    name: {
      given: user.displayName ? user.displayName.split(" ")[0] : "",
      family: user.displayName ? user.displayName.split(" ").slice(1).join(" ") : ""
    },
    contact: { email: user.email || null },
    created_at: now,
    updated_at: now
  });

  console.log(`✅ Created EHR record for ${user.email}`);
});
