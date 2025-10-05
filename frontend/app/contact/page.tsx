'use client'

import React, { useState } from 'react'
import { MailIcon, PhoneIcon, MapPinIcon, SendIcon, ExternalLinkIcon, GithubIcon, LinkedinIcon } from 'lucide-react'
import Link from 'next/link'

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  })

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // For now, just show an alert since we don't have a backend endpoint for this
    alert('Thank you for your message! This is a demo - no actual email will be sent.')
    // Reset form
    setFormData({
      name: '',
      email: '',
      subject: '',
      message: ''
    })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
                <MailIcon className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900">Contact Us</h1>
            </Link>
            <nav className="hidden md:flex space-x-6">
              <Link href="/" className="text-gray-600 hover:text-primary-700 transition-colors">Home</Link>
              <Link href="/about" className="text-gray-600 hover:text-primary-700 transition-colors">About</Link>
              <Link href="/methodology" className="text-gray-600 hover:text-primary-700 transition-colors">Methodology</Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-6">
            Get in Touch
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Have questions about BioNexus? Want to collaborate on research? 
            We'd love to hear from you and discuss how our platform can support your work.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-12">
          {/* Contact Information */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200 h-fit">
              <h3 className="text-xl font-semibold text-gray-900 mb-6">Contact Information</h3>
              
              <div className="space-y-6">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <MailIcon className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Email</h4>
                    <p className="text-gray-600 text-sm">support@bionexus.nasa.gov</p>
                    <p className="text-gray-600 text-sm">research@bionexus.nasa.gov</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <PhoneIcon className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Phone</h4>
                    <p className="text-gray-600 text-sm">+1 (281) 483-0123</p>
                    <p className="text-gray-600 text-xs">Mon - Fri, 9:00 AM - 5:00 PM CST</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <MapPinIcon className="w-5 h-5 text-purple-600" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Address</h4>
                    <p className="text-gray-600 text-sm">
                      NASA Johnson Space Center<br />
                      2101 E NASA Pkwy<br />
                      Houston, TX 77058
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-8 pt-6 border-t border-gray-200">
                <h4 className="font-medium text-gray-900 mb-4">Follow Us</h4>
                <div className="flex space-x-4">
                  <a href="https://github.com/nasa" className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center hover:bg-gray-200 transition-colors">
                    <GithubIcon className="w-5 h-5 text-gray-600" />
                  </a>
                  <a href="https://linkedin.com/company/nasa" className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center hover:bg-gray-200 transition-colors">
                    <LinkedinIcon className="w-5 h-5 text-gray-600" />
                  </a>
                  <a href="https://nasa.gov" className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center hover:bg-gray-200 transition-colors">
                    <ExternalLinkIcon className="w-5 h-5 text-gray-600" />
                  </a>
                </div>
              </div>
            </div>
          </div>

          {/* Contact Form */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200">
              <h3 className="text-xl font-semibold text-gray-900 mb-6">Send us a Message</h3>
              
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                      Full Name *
                    </label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                      placeholder="Enter your full name"
                    />
                  </div>
                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                      Email Address *
                    </label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                      placeholder="Enter your email address"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-2">
                    Subject *
                  </label>
                  <input
                    type="text"
                    id="subject"
                    name="subject"
                    value={formData.subject}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    placeholder="What's this about?"
                  />
                </div>

                <div>
                  <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                    Message *
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    value={formData.message}
                    onChange={handleInputChange}
                    required
                    rows={6}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all resize-none"
                    placeholder="Tell us more about your inquiry..."
                  />
                </div>

                <div className="flex items-center gap-4">
                  <button
                    type="submit"
                    className="inline-flex items-center px-6 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all"
                  >
                    <SendIcon className="w-4 h-4 mr-2" />
                    Send Message
                  </button>
                  <p className="text-sm text-gray-500">
                    We typically respond within 24 hours
                  </p>
                </div>
              </form>
            </div>
          </div>
        </div>

        {/* Additional Resources */}
        <section className="mt-16">
          <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">Additional Resources</h3>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-4">Documentation</h4>
              <p className="text-gray-600 text-sm mb-4">
                Comprehensive guides and API documentation for developers and researchers.
              </p>
              <Link href="/api-docs" className="text-primary-600 hover:text-primary-700 text-sm font-medium inline-flex items-center">
                View Documentation
                <ExternalLinkIcon className="w-4 h-4 ml-1" />
              </Link>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-4">Support Portal</h4>
              <p className="text-gray-600 text-sm mb-4">
                Access help articles, FAQs, and submit support tickets for technical assistance.
              </p>
              <Link href="/support" className="text-primary-600 hover:text-primary-700 text-sm font-medium inline-flex items-center">
                Get Support
                <ExternalLinkIcon className="w-4 h-4 ml-1" />
              </Link>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-4">Community Forum</h4>
              <p className="text-gray-600 text-sm mb-4">
                Join discussions with other researchers and get community support.
              </p>
              <Link href="/community" className="text-primary-600 hover:text-primary-700 text-sm font-medium inline-flex items-center">
                Join Community
                <ExternalLinkIcon className="w-4 h-4 ml-1" />
              </Link>
            </div>
          </div>
        </section>

        {/* FAQ Section */}
        <section className="mt-16">
          <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">Frequently Asked Questions</h3>
          <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200">
            <div className="space-y-8">
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">How can I access the BioNexus API?</h4>
                <p className="text-gray-600 text-sm">
                  The BioNexus API is currently available for NASA researchers and approved collaborators. 
                  Contact us to discuss access requirements and obtain API credentials.
                </p>
              </div>
              
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Can I contribute research papers to the database?</h4>
                <p className="text-gray-600 text-sm">
                  Yes! We welcome contributions of NASA-related bioscience research. Please contact our research team 
                  to discuss the submission process and requirements.
                </p>
              </div>
              
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Is the platform open source?</h4>
                <p className="text-gray-600 text-sm">
                  Parts of BioNexus are open source and available on GitHub. Contact us for information 
                  about contributing to the project or accessing specific components.
                </p>
              </div>
              
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">How often is the database updated?</h4>
                <p className="text-gray-600 text-sm">
                  The BioNexus database is updated continuously as new NASA bioscience publications become available. 
                  Our automated pipeline processes new documents within 24-48 hours of submission.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}