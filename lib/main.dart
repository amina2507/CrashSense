// import 'package:flutter/material.dart';
// import 'package:fluttertoast/fluttertoast.dart';
// import 'package:sqflite_common_ffi/sqflite_ffi.dart';
// import 'package:sqflite_common_ffi_web/sqflite_ffi_web.dart';
// import 'dart:async';
// import 'dart:html' as html;
// import 'videoupload.dart';
// import 'package:email_validator/email_validator.dart';
// import 'package:url_launcher/url_launcher.dart';
// import 'package:flutter_web_plugins/flutter_web_plugins.dart';

// void main() {
//   databaseFactory = databaseFactoryFfiWeb;
//   runApp(const MyApp());
// }

// class MyApp extends StatelessWidget {
//   const MyApp({super.key});

//   @override
//   Widget build(BuildContext context) {
//     return MaterialApp(
//       title: 'Vehicle Collision Detector',
//       debugShowCheckedModeBanner: false,
//       theme: ThemeData(
//         colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
//         useMaterial3: true,
//       ),
//       home: const FrontPage(), // Set FrontPage as the home
//       routes: {
//         '/login': (context) => const LoginPage(),
//         '/video_upload': (context) => VideoUploadScreen(),
//       },
//     );
//   }
// }

// class FrontPage extends StatefulWidget {
//   const FrontPage({super.key});

//   @override
//   _FrontPageState createState() => _FrontPageState();
// }

// class _FrontPageState extends State<FrontPage> {
//   final String _welcomeText = "Welcome to Vehicle Collision Detector";
//   final String _descriptionText =
//       "This application helps to detect vehicle collisions and provides instant alerts for quick responses.";
//   String _displayText = "";
//   String _displayDescription = ""; // To hold the animated description text
//   bool _showDescription = false; // To control description visibility
//   bool _showButton = false; // To control button visibility
//   Timer? _timer;

//   @override
//   void initState() {
//     super.initState();
//     _startAnimation();
//   }

//   void _startAnimation() {
//     int index = 0;

//     _timer = Timer.periodic(const Duration(milliseconds: 100), (timer) {
//       if (index < _welcomeText.length) {
//         setState(() {
//           _displayText += _welcomeText[index];
//           index++;
//         });
//       } else {
//         // Show description after welcome text is fully displayed
//         timer.cancel(); // Stop the timer for welcome text
//         _startDescriptionAnimation(); // Start description animation
//       }
//     });
//   }

//   void _startDescriptionAnimation() {
//     setState(() {
//       _showDescription = true; // Show the description
//     });

//     int index = 0;

//     Timer.periodic(const Duration(milliseconds: 100), (timer) {
//       if (index < _descriptionText.length) {
//         setState(() {
//           _displayDescription += _descriptionText[index];
//           index++;
//         });
//       } else {
//         timer.cancel(); // Stop the timer once the full description is displayed
//         _startButtonAnimation(); // Start button animation after description is complete
//       }
//     });
//   }

//   void _startButtonAnimation() {
//     Timer(const Duration(seconds: 1), () {
//       setState(() {
//         _showButton = true; // Show the button after a brief delay
//       });
//     });
//   }
  

//  void _loadHtmlFile(String fileName) {
//   final url = '$fileName';  
//   html.window.location.href = url;  
// }
//   @override
//   void dispose() {
//     _timer?.cancel(); // Cancel the timer when the widget is disposed
//     super.dispose();
//   }

//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       appBar: AppBar(
//         title: const Text(
//           'Vehicle Collision Detector',
//           textAlign: TextAlign.center,
//           style: TextStyle(
//             color: Color(0xFFFAFAFA),
//             fontWeight: FontWeight.bold,
//           ),
//         ),
//         backgroundColor: Colors.black,
//         centerTitle: true,
//       ),
//       body: Container(
//         decoration: const BoxDecoration(
//           image: DecorationImage(
//             image: AssetImage('assets/background.jpg'),
//             fit: BoxFit.cover,
//           ),
//         ),
//         child: Column(
//           mainAxisAlignment:
//               MainAxisAlignment.center, // Center the content vertically
//           children: [
//             Center(
//               child: Column(
//                 mainAxisAlignment: MainAxisAlignment.center,
//                 children: [
//                   // Display animated welcome text
//                   Text(
//                     _displayText,
//                     style: const TextStyle(
//                       fontSize: 24,
//                       fontWeight: FontWeight.bold,
//                       color: Colors.white,
//                     ),
//                   ),
//                   const SizedBox(
//                       height: 20), // Space between text and description
//                   // Description Text, visible after welcome text
//                   if (_showDescription) ...[
//                     const SizedBox(
//                         height:
//                             20), // Space between welcome text and description
//                     Padding(
//                       padding: const EdgeInsets.symmetric(horizontal: 20.0),
//                       child: Text(
//                         _displayDescription,
//                         textAlign: TextAlign.center,
//                         style: const TextStyle(
//                           fontSize: 16,
//                           color: Colors.white,
//                         ),
//                       ),
//                     ),
//                     const SizedBox(
//                         height: 20), // Space between description and button
//                   ],
//                   // Get Started Button, visible after description
//                   if (_showButton)
//                     ElevatedButton(
//                       onPressed: () {
//                         _loadHtmlFile('index_.html');
//                       },
//                       style: ButtonStyle(
//                         backgroundColor:
//                             MaterialStateProperty.resolveWith<Color>((states) {
//                           if (states.contains(MaterialState.hovered)) {
//                             return Colors
//                                 .green; // Change background color to green on hover
//                           }
//                           return Colors.black; // Default background color
//                         }),
//                         foregroundColor: MaterialStateProperty.all<Color>(
//                             Colors.white), // Text color
//                         padding: MaterialStateProperty.all<EdgeInsets>(
//                           const EdgeInsets.symmetric(
//                               horizontal: 32.0, vertical: 16.0),
//                         ),
//                         textStyle: MaterialStateProperty.all<TextStyle>(
//                           const TextStyle(fontSize: 20), // Text style
//                         ),
//                       ),
//                       child: const Text('Get Started'),
//                     ),
//                 ],
//               ),
//             ),
//           ],
//         ),
//       ),
//       // Footer with copyright information
//       bottomNavigationBar: Container(
//         width: double.infinity, // Make footer take the full width
//         padding: const EdgeInsets.all(16.0),
//         color: const Color.fromARGB(199, 0, 0, 0),
//         child: const Text(
//           '© 2024 Vehicle Collision Detector. All rights reserved.',
//           style: TextStyle(
//             color: Colors.white,
//             fontSize: 14,
//           ),
//           textAlign: TextAlign.center,
//         ),
//       ),
//     );
//   }
// }

// class LoginPage extends StatefulWidget {
//   const LoginPage({super.key});

//   @override
//   _LoginPageState createState() => _LoginPageState();
// }

// class _LoginPageState extends State<LoginPage> {
//   final TextEditingController _usernameController = TextEditingController();
//   final TextEditingController _passwordController = TextEditingController();

//   void _login() {
//     // Dummy credentials
//     const String username = 'Admin';
//     const String password = 'admin123';

//     if (_usernameController.text == username &&
//         _passwordController.text == password) {
//       Navigator.pushReplacement(
//         context,
//         MaterialPageRoute(builder: (context) => VideoUploadScreen()),
//       );
//     } else {
//       // Show toast message
//       Fluttertoast.showToast(
//         msg: "Invalid credentials. Please try again.",
//         toastLength: Toast.LENGTH_SHORT,
//         gravity: ToastGravity.BOTTOM,
//         backgroundColor: Colors.red,
//         textColor: Colors.white,
//         fontSize: 16.0,
//       );
//     }
//   }

//   void _goToSignUp() {
//     Navigator.pushReplacement(
//       context,
//       MaterialPageRoute(builder: (context) => SignUpPage()),
//     );
//   }

//   void _goToForgotPassword() {
//     // Navigate to forgot password page
//   }

//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       appBar: AppBar(
//         title: const Text(
//           'Vehicle Collision Detector',
//           textAlign: TextAlign.center,
//           style: TextStyle(
//             color: Color(0xFFFAFAFA),
//             fontWeight: FontWeight.bold,
//           ),
//         ),
//         backgroundColor: Colors.black,
//         centerTitle: true,
//       ),
//       body: Container(
//         decoration: const BoxDecoration(
//           image: DecorationImage(
//             image: AssetImage('assets/background.jpg'),
//             fit: BoxFit.cover,
//           ),
//         ),
//         child: Center(
//           child: Container(
//             width: MediaQuery.of(context).size.width * 0.35,
//             padding: const EdgeInsets.all(16.0),
//             margin: const EdgeInsets.symmetric(horizontal: 20.0),
//             decoration: BoxDecoration(
//               color: Colors.white.withOpacity(0.7),
//               border: Border.all(color: Colors.deepPurple),
//               borderRadius: BorderRadius.circular(10),
//             ),
//             child: Column(
//               mainAxisSize: MainAxisSize.min,
//               children: <Widget>[
//                 TextField(
//                   controller: _usernameController,
//                   decoration: const InputDecoration(
//                     labelText: 'Username',
//                     border: OutlineInputBorder(),
//                   ),
//                 ),
//                 const SizedBox(height: 16.0),
//                 TextField(
//                   controller: _passwordController,
//                   decoration: const InputDecoration(
//                     labelText: 'Password',
//                     border: OutlineInputBorder(),
//                   ),
//                   obscureText: true,
//                 ),
//                 const SizedBox(height: 20.0),
//                 // Centered Row for Login and Sign Up buttons
//                 Row(
//                   mainAxisAlignment: MainAxisAlignment.center,
//                   children: [
//                     ElevatedButton(
//                       onPressed: _login,
//                       style: ButtonStyle(
//                         backgroundColor:
//                             MaterialStateProperty.resolveWith<Color>((states) {
//                           if (states.contains(MaterialState.hovered)) {
//                             return Colors.green;
//                           }
//                           return Colors.black;
//                         }),
//                         foregroundColor:
//                             MaterialStateProperty.all<Color>(Colors.white),
//                       ),
//                       child: const Text('Login'),
//                     ),
//                     const SizedBox(width: 16.0), // Space between buttons
//                     ElevatedButton(
//                       onPressed: _goToSignUp,
//                       style: ButtonStyle(
//                         backgroundColor: MaterialStateProperty.all<Color>(
//                             Colors.blue), // Different color for Sign Up button
//                         foregroundColor:
//                             MaterialStateProperty.all<Color>(Colors.white),
//                       ),
//                       child: const Text('Sign Up'),
//                     ),
//                   ],
//                 ),
//                 const SizedBox(
//                     height:
//                         16.0), // Space between buttons and forgot password link
//                 // Forgot Password Link
//                 TextButton(
//                   onPressed: _goToForgotPassword,
//                   child: const Text(
//                     'Forgot Password?',
//                     style:
//                         TextStyle(color: Colors.red), // Red color for emphasis
//                   ),
//                 ),
//               ],
//             ),
//           ),
//         ),
//       ),
//       bottomNavigationBar: Container(
//         color: const Color.fromARGB(199, 0, 0, 0),
//         padding: const EdgeInsets.all(16.0),
//         child: const Text(
//           '© 2024 Vehicle Collision Detector. All rights reserved.',
//           textAlign: TextAlign.center,
//           style: TextStyle(
//             color: Colors.white,
//             fontSize: 14.0,
//           ),
//         ),
//       ),
//     );
//   }
// }

// class SignUpPage extends StatefulWidget {
//   const SignUpPage({super.key});

//   @override
//   _SignUpPageState createState() => _SignUpPageState();
// }

// class _SignUpPageState extends State<SignUpPage> {
//   final TextEditingController _firstNameController = TextEditingController();
//   final TextEditingController _lastNameController = TextEditingController();
//   final TextEditingController _phoneController = TextEditingController();
//   final TextEditingController _emailController = TextEditingController();
//   final TextEditingController _usernameController = TextEditingController();
//   final TextEditingController _passwordController = TextEditingController();
//   String? _selectedRole;

//   final List<String> _roles = [
//     'User',
//     'Policeman',
//     'Emergency Service',
//     'Governance'
//   ];

//   void _signUp() {
//     // Simple validation
//     if (_firstNameController.text.isEmpty ||
//         _lastNameController.text.isEmpty ||
//         _phoneController.text.isEmpty ||
//         _emailController.text.isEmpty ||
//         _usernameController.text.isEmpty ||
//         _passwordController.text.isEmpty ||
//         _selectedRole == null) {
//       Fluttertoast.showToast(
//         msg: "Please fill all fields.",
//         toastLength: Toast.LENGTH_SHORT,
//         gravity: ToastGravity.BOTTOM,
//         backgroundColor: Colors.red,
//         textColor: Colors.white,
//         fontSize: 16.0,
//       );
//       return;
//     }

//     void _openHtmlFile(String fileName) async {
//     final url = 'web/html_pages/$fileName'; // Reference to the file inside the web folder
//     if (await canLaunch(url)) {
//       await launch(url);
//     } else {
//       throw 'Could not open $url';
//     }
//   }


//     // Proceed with sign-up logic here (e.g., API call)
//     Fluttertoast.showToast(
//       msg: "Signed up successfully!",
//       toastLength: Toast.LENGTH_SHORT,
//       gravity: ToastGravity.BOTTOM,
//       backgroundColor: Colors.green,
//       textColor: Colors.white,
//       fontSize: 16.0,
//     );

//     // Clear fields after sign-up
//     _firstNameController.clear();
//     _lastNameController.clear();
//     _phoneController.clear();
//     _emailController.clear();
//     _usernameController.clear();
//     _passwordController.clear();
//     setState(() {
//       _selectedRole = null;
//     });
//   }

//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       appBar: AppBar(
//         title: const Text(
//           'Vehicle Collision Detector',
//           textAlign: TextAlign.center,
//           style: TextStyle(
//             color: Color(0xFFFAFAFA),
//             fontWeight: FontWeight.bold,
//           ),
//         ),
//         backgroundColor: Colors.black,
//         centerTitle: true,
//       ),
//       body: Container(
//         decoration: const BoxDecoration(
//           image: DecorationImage(
//             image: AssetImage(
//                 'assets/background.jpg'), // Your background image path
//             fit: BoxFit.cover,
//           ),
//         ),
//         child: Center(
//           child: Container(
//             width:
//                 MediaQuery.of(context).size.width * 0.35, // Set minimum width
//             padding: const EdgeInsets.all(16.0),
//             margin: const EdgeInsets.symmetric(horizontal: 20.0),
//             decoration: BoxDecoration(
//               color: Colors.white.withOpacity(0.7),
//               border: Border.all(color: Colors.deepPurple),
//               borderRadius: BorderRadius.circular(10),
//             ),
//             child: Column(
//               mainAxisSize: MainAxisSize.min,
//               children: <Widget>[
//                 const Text(
//                   'Sign Up',
//                   style: TextStyle(
//                     fontSize: 24,
//                     fontWeight: FontWeight.bold,
//                   ),
//                 ),
//                 const SizedBox(height: 16.0),
//                 TextField(
//                   controller: _firstNameController,
//                   decoration: const InputDecoration(
//                     labelText: 'First Name',
//                     border: OutlineInputBorder(),
//                   ),
//                 ),
//                 const SizedBox(height: 16.0),
//                 TextField(
//                   controller: _lastNameController,
//                   decoration: const InputDecoration(
//                     labelText: 'Last Name',
//                     border: OutlineInputBorder(),
//                   ),
//                 ),
//                 const SizedBox(height: 16.0),
//                 TextField(
//                   controller: _phoneController,
//                   decoration: const InputDecoration(
//                     labelText: 'Phone Number',
//                     border: OutlineInputBorder(),
//                   ),
//                 ),
//                 const SizedBox(height: 16.0),
//                 TextField(
//                   controller: _emailController,
//                   decoration: const InputDecoration(
//                     labelText: 'Email ID',
//                     border: OutlineInputBorder(),
//                   ),
//                 ),
//                 const SizedBox(height: 16.0),
//                 TextField(
//                   controller: _usernameController,
//                   decoration: const InputDecoration(
//                     labelText: 'Username',
//                     border: OutlineInputBorder(),
//                   ),
//                 ),
//                 const SizedBox(height: 16.0),
//                 TextField(
//                   controller: _passwordController,
//                   decoration: const InputDecoration(
//                     labelText: 'Password',
//                     border: OutlineInputBorder(),
//                   ),
//                   obscureText: true,
//                 ),
//                 const SizedBox(height: 16.0),
//                 // Dropdown for Role Selection
//                 DropdownButtonFormField<String>(
//                   value: _selectedRole,
//                   decoration: const InputDecoration(
//                     labelText: 'Select Role',
//                     border: OutlineInputBorder(),
//                   ),
//                   items: _roles.map((String role) {
//                     return DropdownMenuItem<String>(
//                       value: role,
//                       child: Text(role),
//                     );
//                   }).toList(),
//                   onChanged: (String? newValue) {
//                     setState(() {
//                       _selectedRole = newValue;
//                     });
//                   },
//                   validator: (value) => value == null ? 'Select a role' : null,
//                 ),
//                 const SizedBox(height: 20.0),
//                 ElevatedButton(
//                   onPressed: _signUp,
//                   style: ButtonStyle(
//                     backgroundColor:
//                         MaterialStateProperty.resolveWith<Color>((states) {
//                       if (states.contains(MaterialState.hovered)) {
//                         return Colors.green;
//                       }
//                       return Colors.black;
//                     }),
//                     foregroundColor:
//                         MaterialStateProperty.all<Color>(Colors.white),
//                   ),
//                   child: const Text('Sign Up'),
//                 ),
//               ],
//             ),
//           ),
//         ),
//       ),
//       bottomNavigationBar: Container(
//         color: Colors.black,
//         padding: const EdgeInsets.all(16.0),
//         child: const Text(
//           '© 2024 Vehicle Collision Detector. All rights reserved.',
//           textAlign: TextAlign.center,
//           style: TextStyle(color: Colors.white),
//         ),
//       ),
//     );
//   }
// }

import 'package:flutter/material.dart';
import 'dart:html' as html;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadHtmlFile('index_.html');
    });

    // While waiting for the redirection, display an empty scaffold or a loading indicator
    return MaterialApp(
      title: 'Vehicle Collision Detector',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const Scaffold(
        body: Center(
          child: CircularProgressIndicator(), // Optional: Display a loading indicator
        ),
      ),
      routes: {
        '/login': (context) => const LoginPage(),
        '/video_upload': (context) => VideoUploadScreen(),
      },
    );
  }

  // Function to load and redirect to the HTML file
  void _loadHtmlFile(String fileName) {
    final url = fileName;
    html.window.location.href = url;  // Redirects the browser to the HTML file
  }
}

// Dummy pages for routing
class LoginPage extends StatelessWidget {
  const LoginPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Login Page')),
      body: const Center(child: Text('Login Page Content')),
    );
  }
}

class VideoUploadScreen extends StatelessWidget {
  const VideoUploadScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Video Upload')),
      body: const Center(child: Text('Video Upload Page Content')),
    );
  }
}
