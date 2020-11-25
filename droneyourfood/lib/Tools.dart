import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

import 'package:droneyourfood/Profile/Profile.dart';
import 'package:droneyourfood/Shopping/Shopping.dart';

class Tools {
  static void navigatorPopAll(BuildContext context) {
    Navigator.popUntil(context, (Route<dynamic> route) => route.isFirst);
    Navigator.pop(context);
  }

  static void navigatorPushAsRoot(BuildContext context, Route route) {
    navigatorPopAll(context);
    Navigator.push(context, route);
  }

  static double getAppBarHeight(BuildContext context) {
    return MediaQuery.of(context).size.height -
        MediaQuery.of(context).padding.top -
        kToolbarHeight;
  }

  static AppBar genAppBar(BuildContext context, String title) {
    return AppBar(
      title: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(title),
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              ShoppingCart().getButton(context),
              ProfileButton(),
            ],
          )
        ],
      ),
    );
  }

  static void signout(BuildContext context) async {
    debugPrint("Sign-out");
    ShoppingCart.instance.updateFirebaseCart();

    await FirebaseAuth.instance.signOut();
    ShoppingCart.instance.clearCart(); // reload
  }

  static void updateCurrUserInfo(Map<String, dynamic> data) async {
    final String uid = FirebaseAuth.instance.currentUser.uid;
    FirebaseFirestore.instance
        .collection('users')
        .doc(uid)
        .update(data)
        .catchError((e) {
      // the call will fail (reaching this) on the first time the user adds anything
      FirebaseFirestore.instance.collection('users').doc(uid).set(data);
    });
  }

  static void appendCurrUserInfo(String field, List<dynamic> data) async {
    // first is the most recent (it's a pre-append)
    Future<DocumentSnapshot> dShot = FirebaseFirestore.instance
        .collection('users')
        .doc(FirebaseAuth.instance.currentUser.uid)
        .get();
    dShot.then((doc) {
      if (doc.data() != null) {
        Iterable<dynamic> it = doc.data()[field];
        if (it != null) {
          for (var elem in it) data.add(elem);
        }
      }

      updateCurrUserInfo({field: data});
    });
  }

  static void rmUserInfo() async {
    FirebaseFirestore.instance
        .collection('users')
        .doc(FirebaseAuth.instance.currentUser.uid)
        .delete();
  }
}
