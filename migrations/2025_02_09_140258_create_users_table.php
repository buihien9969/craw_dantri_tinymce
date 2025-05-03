<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('users', function (Blueprint $table) {
            $table->id('user_id');
            $table->string('fullname', 255)->nullable();
            $table->date('dob')->nullable();
            $table->string('address', 255)->nullable();
            $table->string('username', 50)->unique();
            $table->string('description', 150)->nullable();
            $table->string('phone', 15)->nullable();
            $table->string('image', 255)->nullable();
            $table->string('email', 100)->unique();
            $table->timestamp('email_verified_at')->nullable();
            $table->string('password', 255)->nullable();
            $table->rememberToken();

            $table->unsignedBigInteger('role_id')->default(4);
            $table->foreign('role_id')->references('role_id')->on('roles')->onDelete('cascade');

            $table->boolean('is_promoted')->default(false);
            $table->integer('violation_count')->default(0);
            $table->timestamp('banned_until')->nullable();

            $table->string('provider')->nullable();
            $table->string('provider_id')->nullable()->unique();

            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('users');
    }
};
