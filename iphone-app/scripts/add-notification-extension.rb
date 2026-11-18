# Adds the "NotificationImages" extension (the picture on notifications) and the
# push notification setting to the Xcode project. Safe to run more than once.
# Run with: ruby scripts/add-notification-extension.rb   (needs: gem install xcodeproj)
require 'xcodeproj'

path = File.expand_path('../ios/App/App.xcodeproj', __dir__)
project = Xcodeproj::Project.open(path)
app = project.targets.find { |t| t.name == 'App' } or abort 'App target not found'

# iPhone only (no iPad version, so no iPad screenshots needed), push entitlement
app.build_configurations.each do |c|
  c.build_settings['TARGETED_DEVICE_FAMILY'] = '1'
  c.build_settings['CODE_SIGN_ENTITLEMENTS'] = 'App/App.entitlements'
end
app_group = project.main_group.find_subpath('App', false)
unless app_group.files.any? { |f| f.path == 'App.entitlements' }
  app_group.new_reference('App.entitlements')
end

name = 'NotificationImages'
ext = project.targets.find { |t| t.name == name }
unless ext
  ext = project.new_target(:app_extension, name, :ios, '15.0', nil, :swift)
  group = project.main_group.new_group(name, name)
  swift = group.new_reference('NotificationService.swift')
  ext.add_file_references([swift])
  group.new_reference('Info.plist')
  singlets = group.new_group('Singlets', 'Singlets')
  Dir.glob(File.expand_path("../ios/App/#{name}/Singlets/*.png", __dir__)).sort.each do |png|
    ref = singlets.new_reference(File.basename(png))
    ext.resources_build_phase.add_file_reference(ref)
  end

  # Put the extension inside the app
  embed = app.copy_files_build_phases.find { |p| p.name == 'Embed Foundation Extensions' } ||
          app.new_copy_files_build_phase('Embed Foundation Extensions')
  embed.symbol_dst_subfolder_spec = :plug_ins
  bf = embed.add_file_reference(ext.product_reference)
  bf.settings = { 'ATTRIBUTES' => ['RemoveHeadersOnCopy'] }
  app.add_dependency(ext)
end

ext.build_configurations.each do |c|
  s = c.build_settings
  s['PRODUCT_BUNDLE_IDENTIFIER'] = 'org.slarchive.app.NotificationImages'
  s['PRODUCT_NAME'] = '$(TARGET_NAME)'
  s['INFOPLIST_FILE'] = "#{name}/Info.plist"
  s['GENERATE_INFOPLIST_FILE'] = 'NO'
  s['SWIFT_VERSION'] = '5.0'
  s['IPHONEOS_DEPLOYMENT_TARGET'] = '15.0'
  s['TARGETED_DEVICE_FAMILY'] = '1'
  s['CODE_SIGN_STYLE'] = 'Automatic'
  s['SKIP_INSTALL'] = 'YES'
  s['MARKETING_VERSION'] = app.build_configurations.first.build_settings['MARKETING_VERSION'] || '1.0'
  s['CURRENT_PROJECT_VERSION'] = app.build_configurations.first.build_settings['CURRENT_PROJECT_VERSION'] || '1'
  s['LD_RUNPATH_SEARCH_PATHS'] = ['$(inherited)', '@executable_path/Frameworks', '@executable_path/../../Frameworks']
end

project.save
puts "Done: #{name} extension and push notifications set up in #{File.basename(path)}"
